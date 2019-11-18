import wbdata as wb
import pandas as pd
import datetime as dt
import time
import math

country_codes = ["DEU", "GRC", "ESP", "CHE"]

#print(wb.get_data("BM.KLT.DINV.CD.WD", "ARB", pandas=True))

file = pd.read_csv("ind.csv")
indicators = file["Indicator Code"]
unique_indicators = list(set(indicators))
unique_indicators.sort()

l = []
from_to = (dt.datetime(1970, 1, 1), dt.datetime(2019, 1, 1))
list_indicators = {}
for i in unique_indicators:
    result = wb.get_data(i, country_codes, pandas=True, data_date=from_to)
    maxi = []
    counter = 0

    for year in range(1970, 2020):
        temp = []
        is_empty = False
        for r in result.keys():
            if r[1] == str(year):
                if r is None or math.isnan(result[r]):
                    is_empty = True
                    break
        if not is_empty:
            counter += 1
            temp.append(year)
        else:
            counter = 0
            if len(maxi) < len(temp):
                maxi = temp[:]
    list_indicators[i] = maxi

print(list_indicators)
