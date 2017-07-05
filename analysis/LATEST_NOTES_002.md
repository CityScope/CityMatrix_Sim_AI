# CityMatrixSim Data Analysis - User Test 002

Here, we seek to analyze some key data metrics from our CityMAItrix Assistant. Use the quick links below to get from section to section.

1. [AI Move Type Choice](#ai-move-type-choice)
- [Density Move Index](#density-move-index)
- [Density Move Values](#density-move-values)
- [AI Weights](#ai-weights)
- [Individual City Scores](#individual-city-scores)
- [Total City Scores](#total-city-scores)

## AI Move Type Choice

Here are the exact move type counts and corresponding percentages.

- Total Cities = 462
- CELL = 247 = 53.4 %
- DENSITY = 215 = 46.6 %

## Density Move Index

For **DENSITY** changes, this is the distribution of the density array index where it acts.

![Alt](data_new/log_170622_pre-test_002_predicted_cities_density_indices.png)

## Density Move Values

And here are the values that the AI tends to suggest.

![Alt](data_new/log_170622_pre-test_002_predicted_cities_density_values.png)

## AI Weights

We can take a look at the user's AI weighting values over time.

![Alt](data_new/log_170622_pre-test_002_predicted_cities_ai_weights.png)

## Individual City Scores

Now, we can take a look at each score value over time. Here, I average over every *N = 2* data points to smooth out our score data.

![Alt](data_new/log_170622_pre-test_002_predicted_cities_indi_scores.png)

## Total City Scores

Now, let's take a look at the **total score value for the city** over time. Again, I average over every *N = 2* data points to smooth out our score data.

![Alt](data_new/log_170622_pre-test_002_predicted_cities_total_score.png)