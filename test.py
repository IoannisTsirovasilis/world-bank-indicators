import wbdata as wb
import pandas as pd
import datetime as dt
import time
import math
import sys

country_codes = ["DEU", "GRC", "ESP", "CHE"]
import numpy as np
#print(wb.get_data("BM.KLT.DINV.CD.WD", "ARB", pandas=True))

file = pd.read_csv("ind.csv")
indicators = file["Indicator Code"]
unique_indicators = list(set(indicators))
unique_indicators.sort()

l = []
from_to = (dt.datetime(1970, 1, 1), dt.datetime(2019, 1, 1))
list_indicators = {}
c = 1
for i in unique_indicators[:10]:
    print(c)
    c += 1
    result = wb.get_data(i, country_codes, pandas=True, data_date=from_to)
    maxi = list()
    counter = 0
    temp_maxi = list()
    for year in reversed(range(1970, 2020)):
        temp = [np.isnan(result[x]) for x in result.keys() if x[1] == str(year)]
        print(temp)
        if True in temp:
            if len(temp_maxi) > len(maxi):
                maxi = temp_maxi[:]
            temp_maxi = list()
            continue
        temp_maxi.append(year)
        #print(temp_maxi)
        #print("MAX: ",maxi)

    list_indicators[i] = maxi[:]

print(list_indicators)
