import wbdata as wb
import pandas as pd
import math

countries = ["DEU", "GRC", "CHE", "ESP"]
file_path = "data/codes.csv"
file = pd.read_csv(file_path)
indicators = file["Indicator Code"]

indicators = list(set(indicators))
indicators.sort()
biggest_cohesive_sets = {}
ind_number = 1
years = list(range(2019, 1959, -1))
completeness_ratios = {}
countries_names = ['Switzerland', 'Germany', 'Spain', 'Greece']
mean_values = []
a = 1
for ind_code in indicators:
    res = wb.get_data(ind_code, country=countries, pandas=True)

    # completeness
    for cn in countries_names:
        # Get current country's years
        keys = [key for key in res.keys() if key[0] == cn]
        # Calculate the list of empty values
        empty_values = [res[key] for key in keys if res[key] is not None and math.isnan(res[key])]
        # Completeness ratio is (n_all_values - n_empty_values) / n_all_values * 100
        ratio = 0
        if len(keys) > 0:
            ratio = (len(keys) - len(empty_values)) / len(keys) * 100
        completeness_ratios["{0} - {1}".format(ind_code, cn)] = ratio

    # cohesivity
    count = 0
    indicators_cohesive_set = []
    for y in years:
        # Get current year's (y) keys for every country
        # e.g keys = [('Switzerland', '2019'), ('Germany', '2019'), ('Spain', '2019'), ('Greece', '2019')]
        # if y = 2019
        keys = [key for key in res.keys() if key[1] == str(y)]
        indicator_values = [math.isnan(res[key]) for key in keys if res[key] is not None]

        # if True is in indicator values it means that we have found at least one "nan" value in a country
        # thus breaking the cohesivity
        # count > 0 is used so as to break cohesivity only if we have found at least one year where for all
        # countries there is an indicator value
        if True in indicator_values and count > 0:
            break
        if True not in indicator_values:
            indicators_cohesive_set.append(y)
            count += 1
    biggest_cohesive_sets[ind_code] = indicators_cohesive_set
    
    non_nan_values = [float(x) for x in res.values if x is not None and not math.isnan(x)]
    if len(non_nan_values) > 0:
        mean_values.append((ind_code, sum(non_nan_values) / len(non_nan_values)))

print(mean_values)
best_ten_mean_values = sorted(mean_values, key=lambda x: x[1], reverse=True)[:10]

for k, v in biggest_cohesive_sets.items():
    print("Indicator: {0} - Biggest Cohesive Set: {1}".format(k, v))

for k, v in completeness_ratios.items():
    print("Indicator - Country: {0} - Completeness Ratio: {1}%".format(k, v))

for k, v in mean_values.items():
    print("Indicator: {0} - Mean: {1}".format(k, v))


