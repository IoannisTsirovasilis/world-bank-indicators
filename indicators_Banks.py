import wbdata as wb
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def output_to_file(file_path, data_structure, key_name="Key", value_name="Value"):
    with open(file_path, "w") as f:
        if isinstance(data_structure, dict):
            for k, v in data_structure.items():
                print("{0}: {1} - {2}: {3}".format(key_name, k, value_name, v))
                f.write("{0},{1}\n".format(k, v))
        elif isinstance(data_structure, list):
            print("Tuple")
            for item in data_structure:
                f.write("{0},{1}\n".format(item[0], item[1]))


def calculate_ratio(indicators_data, country_name):
    # Get current country's years
    keys = [key for key in indicators_data.keys() if key[0] == country_name]
    # Calculate the list of empty values
    empty_values = [indicators_data[key] for key in keys if indicators_data[key] is not None
                    and math.isnan(indicators_data[key])]
    # Completeness ratio is (n_all_values - n_empty_values) / n_all_values * 100
    ratio = 0
    if len(keys) > 0:
        ratio = (len(keys) - len(empty_values)) / len(keys) * 100
    return ratio


def calculate_biggest_cohesive_set(indicators_data, years):
    count = 0
    indicators_cohesive_set = []
    for y in years:
        # Get current year's (y) keys for every country
        # e.g keys = [('Switzerland', '2019'), ('Germany', '2019'), ('Spain', '2019'), ('Greece', '2019')]
        # if y = 2019
        keys = [key for key in indicators_data.keys() if key[1] == str(y)]
        indicator_values = [math.isnan(indicators_data[key]) for key in keys if indicators_data[key] is not None]

        # if True is in indicator values it means that we have found at least one "nan" value in a country
        # thus breaking the cohesivity
        # count > 0 is used so as to break cohesivity only if we have found at least one year where for all
        # countries there is an indicator value
        if True in indicator_values and count > 0:
            break
        if True not in indicator_values:
            indicators_cohesive_set.append(y)
            count += 1
    return indicators_cohesive_set


def process_indicators(indicators, countries, countries_names):
    biggest_cohesive_sets = {}
    years = list(range(2019, 1959, -1))
    completeness_ratios = {}
    mean_values = []
    a = 1
    for ind_code in indicators:
        res = wb.get_data(ind_code, country=countries, pandas=True)
        if a % 100 == 0:
            print(a)
        a += 1
        # completeness
        for cn in countries_names:
            completeness_ratios["{0} - {1}".format(ind_code, cn)] = calculate_ratio(res, cn)

        # cohesivity
        biggest_cohesive_sets[ind_code] = calculate_biggest_cohesive_set(res, years)

        non_nan_values = [float(x) for x in res.values if x is not None and not math.isnan(x)]
        if len(non_nan_values) > 0:
            mean_values.append((ind_code, sum(non_nan_values) / len(non_nan_values)))
        else:
            mean_values.append((ind_code, 0))

    print(mean_values)
    best_ten_mean_values = sorted(mean_values, key=lambda x: x[1], reverse=True)[:10]

    output_to_file("files/biggest_cohesive_sets.txt", biggest_cohesive_sets, "Indicator", "Biggest Cohesive Set")
    output_to_file("files/completeness_ratios.txt", completeness_ratios, "Indicator - Country", "Completeness Ratio")
    output_to_file("files/best_ten_indicators.txt", best_ten_mean_values, "Indicator", "Mean")


def calculate_correlations(indicators, countries):
    api_data = wb.get_dataframe(indicators, country=countries)
    api_data = api_data.reset_index()
    greece_data = api_data[api_data['country'] == 'Greece']
    germany_data = api_data[api_data['country'] == 'Germany']
    swiss_data = api_data[api_data['country'] == 'Switzerland']
    spain_data = api_data[api_data['country'] == 'Spain']

    corr_greece = greece_data.corr()
    corr_germany = germany_data.corr()
    corr_swiss = swiss_data.corr()
    corr_spain = spain_data.corr()
    result = {"Greece": corr_greece, "Germany": corr_germany, "Switzerland": corr_swiss, "Spain": corr_spain}
    return result


def plot_results(countries):
    fig, axs = plt.subplots(2, 2, figsize=(20, 15))
    plt.suptitle('Correlation heatmap for the selected indicator codes', fontsize=20)
    mask = np.zeros_like(countries["Greece"], dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    sns.heatmap(countries["Greece"], mask=mask, cmap=cmap, linewidths=.5, square=True, ax=axs[0][0])
    sns.heatmap(countries["Germany"], mask=mask, cmap=cmap, linewidths=.5, square=True, ax=axs[0][1])
    sns.heatmap(countries["Switzerland"], mask=mask, cmap=cmap, linewidths=.5, square=True, ax=axs[1][0])
    sns.heatmap(countries["Spain"], mask=mask, cmap=cmap, linewidths=.5, square=True, ax=axs[1][1])

    axs[0][0].set_title('Greece', fontsize=18)
    axs[0][1].set_title('Germany', fontsize=18)
    axs[1][0].set_title('Switzerland', fontsize=18)
    axs[1][1].set_title('Spain', fontsize=18)

    plt.subplots_adjust(hspace=0.6)
    plt.show()


def main():
    countries = ["DEU", "GRC", "CHE", "ESP"]
    file_path = "data/codes.csv"
    file = pd.read_csv(file_path)
    indicators = file["Indicator Code"]

    indicators = list(set(indicators))
    indicators.sort()
    countries_names = ['Switzerland', 'Germany', 'Spain', 'Greece']

    # This is used to generate the 3 files in files/ directory. No need to rerun it unless you want to extract
    # different results
    # process_indicators(indicators, countries, countries_names)

    content = pd.read_csv("files/best_indicators_names.txt", header=None)
    correlations = calculate_correlations(dict(zip(content[0], content[1])), countries)

    plot_results(correlations)


if __name__ == "__main__":
    main()




