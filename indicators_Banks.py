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


def plot_results(countries, countries_names):
    for cn in countries_names:
        fig, axs = plt.subplots()
        mask = np.zeros_like(countries[cn], dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        cmap = sns.diverging_palette(220, 20, as_cmap=True)
        sns.heatmap(countries[cn], mask=mask, cmap=cmap, linewidths=.5, square=True)
        axs.set_title(cn)
        plt.show()


def plot_best_indicators(countries, countries_names):
    inds = {
                "NY.GDP.MKTP.PP.CD": "GDP PPP (current international $)",
                "NE.DAB.TOTL.KD": "Gross national expenditure (constant 2010 US$)"
            }

    for i, v in inds.items():
        fig, ax = plt.subplots()
        res = wb.get_data(i, country=countries, pandas=True)
        x = list(range(2019, 1959, -1))
        colors = ['r', 'k', 'y', 'b']
        c = 0
        for cn in countries_names:
            y = []
            for year in x:
                data = [res[k] for k in res.keys() if k[1] == str(year) and k[0] == cn]
                y.append(data[0])
            ax.plot(x, y, color=colors[c], label=cn)
            c += 1

        plt.title('Line Graph')
        plt.xlabel('Year')
        plt.ylabel(v)
        ax.legend()
        plt.show()


def plot_mean_completeness(countries_names):
    results = {}
    for c in countries_names:
        results[c] = 0
    with open("files/completeness_ratios.txt", "r") as f:
        content = f.readlines()
    length = len(content) / 4
    for line in content:
        temp = line.split(",")
        for c in countries_names:
            if c in temp[0]:
                results[c] += float(temp[1]) / length
    ind = range(len(countries_names))
    width = 0.35
    plt.bar(ind, results.values(), width)

    plt.ylabel('Percentage')
    plt.title('Average Completeness')
    plt.xticks(ind, countries_names)
    plt.yticks(range(0, 101, 5))

    plt.show()


def plot_best_ten_indicators_mean_completeness():
    with open("files/best_ten_indicators.txt", "r") as f:
        content = f.readlines()
    best_ten_indicators = [x.split(",")[0] for x in content]

    with open("files/biggest_cohesive_sets.txt", "r") as f:
        content = f.readlines()

    results = {}
    for line in content:
        index = line.index(",")
        line = line.replace(",", ";", 1)
        ind = line.split(";")
        if ind[0] in best_ten_indicators:
            temp = ind[1].replace("[", "").replace("]", "").replace(" ", "").split(",")
            results[ind[0]] = [int(x) for x in temp]
    x = []
    y = []
    c = 0
    for k, v in results.items():
        for i in v:
            if c % 2 == 0:
                x.append("\n{0}".format(k))
            else:
                x.append(k)
            y.append(i)
        c += 1
    fig, ax = plt.subplots()

    ax.plot(x, y, 'o')

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
    process_indicators(indicators, countries, countries_names)

    content = pd.read_csv("files/best_indicators_names.txt", header=None)
    correlations = calculate_correlations(dict(zip(content[0], content[1])), countries)

    plot_results(correlations, countries_names)

    plot_best_indicators(countries, countries_names)

    plot_mean_completeness(countries_names)

    plot_best_ten_indicators_mean_completeness()


if __name__ == "__main__":
    main()




