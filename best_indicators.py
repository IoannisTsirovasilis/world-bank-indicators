import wbdata as wb
import pandas as pd
import datetime as dt
import time
import math
import sys

country_codes = ["DEU", "GRC", "ESP", "CHE"]

#print(wb.get_data("BM.KLT.DINV.CD.WD", "ARB", pandas=True))

file = pd.read_csv("ind.csv")
indicators = file["Indicator Code"]
unique_indicators = list(set(indicators))
unique_indicators.sort()

l = []
from_to = (dt.datetime(1970, 1, 1), dt.datetime(2019, 1, 1))
best_indicators = []
c = 1
for i in unique_indicators:
    print(c)
    c += 1
    result = wb.get_data(i, country_codes, pandas=True, data_date=from_to)
    temp = [type(result[x]) != type(float) for x in result.keys()]
    if len(best_indicators) < 10:
        best_indicators.append({i:})


print(best_indicators)
