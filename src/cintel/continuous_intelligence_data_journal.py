"""
continuous_intelligence_data_journal.py - Project script (example).

Author: Aaron Gillespie
Date: 2026-04

Data Journal System Status

- Data represents recent observations from my Data Journal.
- Each row represents one week tracked.

- The CSV file includes a number of columns, but the key ones for this project are:
  - id: the week number in the journal
  - summaries: the number of summaries written that week
  - sleep_duration: the average sleep duration in hours for that week
    - Used as a proxy for all Oura-tracked data
- pains: the number of individually tracked pains that week
- workouts: the number of workouts tracked that week
- youtube: the number of YouTube videos watched that week
    - Per my captsone project, this actually matters!
- other_media: a feature added in this project to aggregate other media consumption
    - A proxy for if I'm tracking things, assuming I engage with at least SOME media
- youtube_to_other_media_ratio: a feature added in this project to compare YouTube consumption to other media consumption
    - Under the assumption that "YouTube" is more likely to be "mindless", which I'd like to minimize.

Purpose

- Read system metrics from a CSV file.
- Apply multiple continuous intelligence techniques learned earlier:
  - anomaly detection
  - signal design
  - simple drift-style reasoning
- Summarize the system's current state.
    - In this case, the "system" is my overall health and wellness as tracked in my Data Journal.
    - It **also** entails the Data Journal system itself & how well I'm using it.
- Save the resulting system assessment as a CSV artifact.
- Log the pipeline process to assist with debugging and transparency.

Questions to Consider

- What signals best summarize the health of a system?
- When multiple indicators change at once, how should we interpret the system's state?
- How can monitoring data support operational decisions?

Paths (relative to repo root)

    INPUT FILE: data/system_metrics_data_journal.csv
    OUTPUT FILE: artifacts/system_assessment_data_journal.csv

Terminal command to run this file from the root project folder

    uv run python -m cintel.continuous_intelligence_data_journal
"""

# === DECLARE IMPORTS ===

import logging
from pathlib import Path
from typing import Final

import polars as pl
from datafun_toolkit.logger import get_logger, log_header, log_path

# === CONFIGURE LOGGER ===

LOG: logging.Logger = get_logger("P6", level="DEBUG")

# === DEFINE GLOBAL PATHS ===

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
ARTIFACTS_DIR: Final[Path] = ROOT_DIR / "artifacts"

DATA_FILE: Final[Path] = DATA_DIR / "system_metrics_data_journal.csv"
OUTPUT_FILE_META: Final[Path] = (
    ARTIFACTS_DIR / "system_assessment_data_journal_meta.csv"
)
OUTPUT_FILE_AARON: Final[Path] = (
    ARTIFACTS_DIR / "system_assessment_data_journal_aaron.csv"
)

# === DEFINE THRESHOLDS ===

# Analysts need to know their data and
# choose thresholds that make sense for their specific use case.

# DATA JOURNAL HEALTH THRESHOLDS
DEGRADED_SUMMARY_MIN: Final[float] = (
    6.0  # missing at least 1 summary per week is considered "degraded"
)
WARNING_MEDIA_COUNT_MIN: Final[int] = (
    2  # expecting I engage at least 2 non-YouTube media sources per week
)

# PERSONAL HEALTH WEEKLY THRESHOLDS
DEGRADED_SLEEP_HOURS_MIN_AVG: Final[float] = 6.5
DEGRADED_SLEEP_HOURS_MAX_AVG: Final[float] = 8.5
DEGRADED_PAINS_MAX_COUNT: Final[int] = 3
DEGRADED_WORKOUTS_MIN_COUNT: Final[int] = 2
DEGRADED_YOUTUBE_MAX_COUNT: Final[int] = 70  # 10 per day, which feels like a LOT
DEGRADED_MINDLESS_VIEWING_RATIO_MAX: Final[float] = (
    0.1  # expecting at least 10% of media consumption to be non-YouTube
)

# NOTE REGARDING YOUTUBE RATIO:
# The counting mechanic for YouTube is VIDEOS WATCHED,
# which includes shorts, which can add up quickly.
# The counting mechanic for "other media" is SESSIONS,
# and sessions are typically longer and less likely to be "mindless" than YouTube videos.
# So - this ratio is a gross proxy at best.

# === DEFINE THE MAIN FUNCTION ===


def main() -> None:
    """Run the pipeline.

    log_header() logs a standard run header.
    log_path() logs repo-relative paths (privacy-safe).
    """
    log_header(LOG, "CINTEL")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "ROOT_DIR", ROOT_DIR)
    log_path(LOG, "DATA_FILE", DATA_FILE)
    log_path(LOG, "OUTPUT_FILE_META", OUTPUT_FILE_META)
    log_path(LOG, "OUTPUT_FILE_AARON", OUTPUT_FILE_AARON)

    # Ensure artifacts directory exists
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    log_path(LOG, "ARTIFACTS_DIR", ARTIFACTS_DIR)

    # ----------------------------------------------------
    # STEP 1: READ SYSTEM METRICS
    # ----------------------------------------------------
    df = pl.read_csv(DATA_FILE)

    LOG.info(f"STEP 1. Loaded {df.height} system records")

    # ----------------------------------------------------
    # STEP 2: DESIGN SIGNALS
    # ----------------------------------------------------
    # This step connects to Module 3: Signal Design.
    # Create useful signals derived from raw system metrics.

    LOG.info("STEP 2. Designing signals from raw metrics...")

    df = df.with_columns(
        [
            (
                pl.col("book") + pl.col("tv") + pl.col("movie") + pl.col("videogame")
            ).alias("other_media"),
            (
                # To avoid division by zero, only calculate the ratio when there is at least some other media consumption.
                pl.when(
                    (
                        pl.col("book")
                        + pl.col("tv")
                        + pl.col("movie")
                        + pl.col("videogame")
                    )
                    > 0
                )
                .then(
                    pl.col("youtube")
                    / (
                        pl.col("book")
                        + pl.col("tv")
                        + pl.col("movie")
                        + pl.col("videogame")
                    )
                )
                .otherwise(pl.lit(0))
            ).alias("youtube_to_other_media_ratio"),
        ]
    )

    # ----------------------------------------------------
    # STEP 3: DETECT ANOMALIES
    # ----------------------------------------------------
    # This step connects to Module 2: Anomaly Detection.
    # Check whether signal values exceed reasonable thresholds.

    # STEP 3A: DATA JOURNAL META METRICS
    # Check whether the Data Journal itself is "healthy" - i.e. am I engaging enough

    LOG.info("STEP 3. Checking for anomalies in Data Journal signals...")

    meta_df = df.filter(
        (pl.col("summaries") < DEGRADED_SUMMARY_MIN)
        | (pl.col("other_media") < WARNING_MEDIA_COUNT_MIN)
    )
    LOG.info(
        f"STEP 3A. Using thresholds: DEGRADED_SUMMARY_MIN={DEGRADED_SUMMARY_MIN}, "
        f"WARNING_MEDIA_COUNT_MIN={WARNING_MEDIA_COUNT_MIN}"
    )

    LOG.info(f"STEP 3. Anomalies detected: {meta_df.height}")

    # STEP 3B: PERSONAL HEALTH METRICS
    # Check whether my personal health signals are indicating a degraded operational state for Aaron
    LOG.info("STEP 3B. Checking for anomalies in signals about Aaron...")

    aaron_df = df.filter(
        (pl.col("sleep_duration") < DEGRADED_SLEEP_HOURS_MIN_AVG)
        | (pl.col("sleep_duration") > DEGRADED_SLEEP_HOURS_MAX_AVG)
        | (pl.col("pains") > DEGRADED_PAINS_MAX_COUNT)
        | (pl.col("workouts") < DEGRADED_WORKOUTS_MIN_COUNT)
        | (pl.col("youtube") > DEGRADED_YOUTUBE_MAX_COUNT)
        | (pl.col("youtube_to_other_media_ratio") > DEGRADED_MINDLESS_VIEWING_RATIO_MAX)
    )
    LOG.info(
        f"STEP 3B. Using thresholds: DEGRADED_SLEEP_HOURS_MIN_AVG={DEGRADED_SLEEP_HOURS_MIN_AVG}, "
        f"DEGRADED_SLEEP_HOURS_MAX_AVG={DEGRADED_SLEEP_HOURS_MAX_AVG}, "
        f"DEGRADED_PAINS_MAX_COUNT={DEGRADED_PAINS_MAX_COUNT}, "
        f"DEGRADED_WORKOUTS_MIN_COUNT={DEGRADED_WORKOUTS_MIN_COUNT}, "
        f"DEGRADED_YOUTUBE_MAX_COUNT={DEGRADED_YOUTUBE_MAX_COUNT}, "
        f"DEGRADED_MINDLESS_VIEWING_RATIO_MAX={DEGRADED_MINDLESS_VIEWING_RATIO_MAX}"
    )

    LOG.info(f"STEP 3B. Anomalies detected: {aaron_df.height}")

    # ----------------------------------------------------
    # STEP 4: SUMMARIZE CURRENT SYSTEM STATE
    # ----------------------------------------------------
    # This step brings together ideas from earlier modules:
    # - Module 3: Signal Design
    # - Module 2: Anomaly Detection
    # It then adds the main goal of Module 6:
    # assess the overall state of the system.

    # NOTE: recipes for column creation and filtering
    # can be done in place as we add signals and logic to a DataFrame.
    # When logic is more complex, it can be helpful to
    # break it into multiple steps/recipes
    # for readability and debugging as shown previously.

    LOG.info("STEP 4A. Summarizing Data Journal state from monitored signals...")

    summary_meta_df = df.select(
        [
            pl.col("summaries").mean().alias("avg_summaries"),
            pl.col("other_media").mean().alias("avg_other_media"),
        ]
    )

    # Add a simple assessment label
    summary_meta_df = summary_meta_df.with_columns(
        pl.when(
            (pl.col("avg_summaries") < DEGRADED_SUMMARY_MIN)
            | (pl.col("avg_other_media") < WARNING_MEDIA_COUNT_MIN)
        )
        .then(pl.lit("DEGRADED JOURNAL"))
        .otherwise(pl.lit("HEALTHY JOURNAL"))
        .alias("journal_meta_state")
    )

    LOG.info("STEP 4A. Data Journal assessment completed")

    # STEP 4B: PERSONAL HEALTH ASSESSMENT
    # Assess whether the signals about my behavior indicate a "DEGRADED"
    LOG.info("STEP 4B. Summarizing Aaron state from monitored signals...")

    summary_aaron_df = df.select(
        [
            pl.col("sleep_duration").mean().alias("avg_sleep_duration"),
            pl.col("pains").mean().alias("avg_pains"),
            pl.col("workouts").mean().alias("avg_workouts"),
            pl.col("youtube").mean().alias("avg_youtube"),
            pl.col("other_media").mean().alias("avg_other_media"),
            pl.col("youtube_to_other_media_ratio")
            .mean()
            .alias("avg_youtube_to_other_media_ratio"),
        ]
    )

    # Add a simple assessment label
    summary_aaron_df = summary_aaron_df.with_columns(
        pl.when(
            (pl.col("avg_sleep_duration") < DEGRADED_SLEEP_HOURS_MIN_AVG)
            | (pl.col("avg_sleep_duration") > DEGRADED_SLEEP_HOURS_MAX_AVG)
            | (pl.col("avg_pains") > DEGRADED_PAINS_MAX_COUNT)
            | (pl.col("avg_workouts") < DEGRADED_WORKOUTS_MIN_COUNT)
            | (pl.col("avg_youtube") > DEGRADED_YOUTUBE_MAX_COUNT)
            | (
                pl.col("avg_youtube_to_other_media_ratio")
                > DEGRADED_MINDLESS_VIEWING_RATIO_MAX
            )
        )
        .then(pl.lit("DEGRADED AARON"))
        .otherwise(pl.lit("HEALTHY AARON"))
        .alias("aaron_health_state")
    )

    LOG.info("STEP 4B. Aaron assessment completed")

    # ----------------------------------------------------
    # STEP 5: SAVE SYSTEM ASSESSMENT
    # ----------------------------------------------------
    summary_meta_df.write_csv(OUTPUT_FILE_META)
    summary_aaron_df.write_csv(OUTPUT_FILE_AARON)

    LOG.info(
        f"STEP 5. Wrote system assessment file: {OUTPUT_FILE_META} and {OUTPUT_FILE_AARON}"
    )

    LOG.info("========================")
    LOG.info("Pipeline executed successfully!")
    LOG.info("========================")
    LOG.info("END main()")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()
