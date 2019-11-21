import wbdata as wb
import numpy as np
import pandas as pd


countries = [ "DEU","GRC","CHE","ESP"]
file_path = "C:\\Users\\Ioannis\\Desktop\\world-bank-indicators\\data\\codes.csv"
file = pd.read_csv(file_path)
indicators = file["Indicator Code"]

indicators = list(set(indicators))
print(len(indicators))
indicators.sort()
print(indicators)

indicators_of_GRC = {}
for ind_code in indicators:
    count = 0
    res = wb.get_data( ind_code , country="GRC", pandas=True)
    for i in range(len(res)):
        if res[i] != np.nan:
            count +=1
        else:
            break
        break
        
    indicators_of_GRC[ind_code] = count
    print(indicators_of_GRC)


