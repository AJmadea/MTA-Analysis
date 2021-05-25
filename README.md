# MTA-Analysis

The original goal for this project was to parse the amount of rides each station for each date from the MTA website.  
A simple algorithm did not work, but the ML clustering algorithm DBSCAN has proven to be effective.
DBSCAN parameters were optimized compared against the estimated values from the MTA.

One nice visualization is how COVID-19 affected MTA ridership [found here](https://github.com/AJmadea/MTA-Analysis/blob/master/plotlyGraphs/entries_over_time_inclusive_of_05_8_2021.png "Image ref").
The top stations that were effected by COVID-19 can be [found here](https://github.com/AJmadea/MTA-Analysis/blob/master/data_by_date/top_covid_change.csv).
