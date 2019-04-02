# -*- coding: utf-8 -*-

import pandas as pd, numpy as np, statsmodels.api as sm
import matplotlib.pyplot as plt, matplotlib.cm as cm, matplotlib.font_manager as fm
from scipy.stats import pearsonr, ttest_rel
import numpy as np
import nominatim
import requests
import time
import multiprocessing as mp

# function to convert string to float and handle empty string as NaN
def to_float(string_value):
    if (isinstance(string_value,float)):
      return string_value
    string_value = string_value.strip()
    return np.float(string_value) if string_value else np.nan

all_listings = pd.read_csv('data/usa.csv',header=[0])
all_listings = all_listings[all_listings['baths'] != 'baths']
all_listings.to_csv('data/usa-fixed.csv')

# load the full, combined data set, converting numeric columns to float using our function
# only the floats are here
converters = {'price':to_float, 
              'beds':to_float, 
              'sqft':to_float, 
              'longitude':to_float, 
              'latitude':to_float}

all_listings = pd.read_csv('data/usa-fixed.csv', converters=converters)

all_listings = all_listings.rename(columns={ \
     'price':'rent','craigId':'pid','size':'sqft','date':'date2','beds':'bedrooms'})
all_listings = all_listings.rename(columns={'postDate':'date'})

print(all_listings['pid'].count())
date_is_null = list(all_listings['date'].isnull())
lat_is_null = list(all_listings['latitude'].isnull())
long_is_null = list(all_listings['longitude'].isnull())
some_null = date_is_null and lat_is_null and long_is_null
date_remove = np.array(date_is_null).nonzero()[0].tolist()
lat_remove = np.array(lat_is_null).nonzero()[0].tolist()
long_remove = np.array(long_is_null).nonzero()[0].tolist()
# rows_remove = np.array(some_null).nonzero()[0].tolist()
rows_remove = list(set(date_remove + lat_remove + long_remove))
print("Null date: ",sum(date_is_null),len(date_remove))
print("Null lat: ",sum(lat_is_null),len(lat_remove))
print("Null long: ",sum(long_is_null),len(long_remove))
print("Null some: ",sum(some_null),len(rows_remove))
all_listings.drop(rows_remove, inplace=True)

# number of rows in the full data set (includes dupes/re-posts)
print(all_listings['pid'].count())
print(list(all_listings.columns.values))

# de-dupe data set and create a new dataframe to hold the unique listings
unique_listings = pd.DataFrame(all_listings.drop_duplicates(subset='pid', inplace=False))
len(unique_listings)

# thorough listings are unique listings with rent and sqft data
thorough_listings = pd.DataFrame(unique_listings)
thorough_listings = thorough_listings[thorough_listings['rent'] > 0]

# for comparison, what are the counts of the differents sets?
print('Count of all listings:', len(all_listings))
print('Count of unique listings:', len(unique_listings))
print('Count of thorough listings:', len(thorough_listings))

# in this cell, define the values by which we will filter the 3 columns
upper_percentile = 0.998
lower_percentile = 0.002

# how many rows would be within the upper and lower percentiles?
upper = int(len(thorough_listings) * upper_percentile)
lower = int(len(thorough_listings) * lower_percentile)

# get the rent values at the upper and lower percentiles
rent_sorted = thorough_listings['rent'].sort_values(ascending=True, inplace=False)
upper_rent = rent_sorted.iloc[upper]
lower_rent = rent_sorted.iloc[lower]

print('valid rent range:', [lower_rent, upper_rent])

rent_mask = (thorough_listings['rent'] > lower_rent) & (thorough_listings['rent'] < upper_rent)
# filter the thorough listings according to these masks
filtered_listings = pd.DataFrame(thorough_listings[rent_mask])

with open('data/usa-filt.csv', 'w') as f:
  filtered_listings.to_csv(f, header=True)
