# Continuous Intelligence

This site provides documentation for this project.
Use the navigation to explore module-specific materials.

## Custom Project - Data Journal & Aaron Behavioral Health Tracking

### Dataset

The data I'm using here is my own Data Journal data, documented extensively [here](https://datajournal.guide), aggregated to the week. This is the same dataset I used for my recent [CSIS Capstone project](https://github.com/aarongilly/csis_capstone/blob/main/notebook.ipynb). It contains a number of columns that track my behavior over time. The relevant ones for this project are:

- `summaries` - the number of "Daily recap" journal inputs per week
- `sleep_duration` - average sleep duration for the week
- `pains` - count of individually tracked pains
- `workouts` - count of individually tracked workouts
- `youtube` - count of YouTube videos watched
- `tv`, `book`, `movie`, `videogame` - counts of SESSIONS in which I engaged with that type of media

### Signals

I created two derived signals.

- `other_media` - summing up the total non-YouTube media sessions
- `youtube_to_other_media_ratio` - YouTube videos watched / `other_media` sessions

### Experiments

Arguably the biggest experiment I did here was utilize one data source to assess the health of two separate things - the Data Journal itself and the behavior of the guy who uses it.

I also experimented with adding & removing the YouTube metrics, as I realized that was the metric that was pushing `HEALTHY AARON` into `DEGRADED AARON` territory.

### Results
The data revealed an average of averages across the weeks for the number of `summary`s and average of counts of `pains` and other metrics.

On the whole:

- The Data Journal META health is quite good!
- The Aaron behavioral health is... okay
  - If you take out YouTube it's pretty good!

Fun (maybe?) fact: per [my capstone project Juypter Notebook](https://github.com/aarongilly/csis_capstone/blob/main/notebook.ipynb), YouTube video view count is the 2nd strongest predictor of having "good" days.

### Interpretation

My Data Journal is functioning optimally – which is good because otherwise I wouldn't feel justified [teaching others how to build their own Data Journal](https://datajournal.guide)

My personal behavior is good, less the YouTube. YouTube is a double-edged sword. It provides great value, but also can be a mindless time-suck. It's changed all of our lives, partly for the better, and partly for the worse.

## Project Documentation Pages (docs/)

- **Home** - this documentation landing page
- **Project Instructions** - instructions specific to this module
- **Glossary** - project terms and concepts

## Additional Resources

- [Suggested Datasets](https://denisecase.github.io/pro-analytics-02/reference/datasets/cintel/)
