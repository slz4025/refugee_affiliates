#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[43]:


# city features
city_data = pd.read_csv('./merged_city_data_normalized_with_employment.csv').set_index('GeoID')
# incomplete dataset, but has place names
city_data_with_names = pd.read_csv('./merged_city_data_normalized.tsv',
        sep='\t')#.set_index('GeoID')
#city_data_with_names = city_data_with_names.groupby(city_data_with_names.index).first()
#print(list(city_data_with_names.columns.values))
place_map = pd.Series(city_data_with_names['Place Name'].values,
        index=city_data_with_names['GeoID']).to_dict()
# affiliate cities and their geoids
aff_cities = pd.read_csv('./Affiliate-City-to-Id2.csv', names=['Place Name',
    'GeoID']) #.set_index('GeoID')
aff_map = pd.Series(aff_cities['Place Name'].values,
    index=aff_cities['GeoID']).to_dict()

# TODO include population in ranking

job_features = [
    'Indeed job count normalized min_max_normalized'
]

pos_economic_features = [
    'Employment to population ratio percentage min_max_normalized',
    'Employment Rate Prediction min_max_normalized'
]

neg_economic_features = [
    'Number of people below the poverty level normalized min_max_normalized',
]

food_features = [
    'SNAP-authorized Stores per 1000 people (2016) min_max_normalized',
    'Farmers Markets per 1000 people (2016) min_max_normalized',
    'Farmer Markets with SNAP per 1000 people (2016) min_max_normalized',
    'Farmer Markets with WIC per 1000 people (2016) min_max_normalized',
    'Farmer Markets with WIC Cash per 1000 people (2016) min_max_normalized',
    'Farmer Markets with SFMNP per 1000 people (2016) min_max_normalized'
]

transit_features = [
    'Public transportation proportion min_max_normalized',
    'Proportion of public transit to work under 30 minutes min_max_normalized'
]

housing_features = [
    'Affordable housing in market min_max_normalized',
    'Craigslist affordable house count normalized min_max_normalized'
]

education_features = [
    'Number of people with a bachelors degree or higher normalized min_max_normalized'
]

diversity_features = [
    'Simpsons diversity score min_max_normalized',
]


# weighing
job_weight = 1
pos_economic_weight = 1
neg_economic_weight = -1
food_weight = 1
transit_weight = 1
housing_weight = 1
education_weight = 1
diversity_weight = 1

# normalize by size of each feature-class

job_sums = job_weight * city_data[city_data.columns[\
        city_data.columns.isin(job_features)]].sum(axis=1)\
        / len(job_features)
pos_economic_sums = pos_economic_weight * city_data[city_data.columns[\
        city_data.columns.isin(pos_economic_features)]].sum(axis=1)\
        / len(pos_economic_features)
neg_economic_sums = neg_economic_weight * city_data[city_data.columns[\
        city_data.columns.isin(neg_economic_features)]].sum(axis=1)\
        / len(neg_economic_features)
food_sums = food_weight * city_data[city_data.columns[\
        city_data.columns.isin(food_features)]].sum(axis=1)\
        / len(food_features)
transit_sums = transit_weight * city_data[city_data.columns[\
        city_data.columns.isin(transit_features)]].sum(axis=1)\
        / len(transit_features)
housing_sums = housing_weight * city_data[city_data.columns[\
        city_data.columns.isin(housing_features)]].sum(axis=1)\
        / len(housing_features)
education_sums = education_weight * city_data[city_data.columns[\
        city_data.columns.isin(education_features)]].sum(axis=1)\
        / len(education_features)
diversity_sums = diversity_weight * city_data[city_data.columns[\
        city_data.columns.isin(diversity_features)]].sum(axis=1)\
        / len(diversity_features)

city_scores = job_sums + pos_economic_sums + neg_economic_sums + food_sums + transit_sums \
    + housing_sums + education_sums + diversity_sums

city_scores.sort_values(ascending=False, inplace=True)

to_display = 10
for geoid, score in city_scores[:to_display].iteritems():
    print("Score: {:.2f}\tGeoID: {}\tPlace Name: {}\tAffiliate Status: {}"\
    .format(score, geoid, place_map[geoid],\
    geoid in aff_map))

print()
#print(city_data_with_names.loc[city_data_with_names['GeoID'] == 845970])
print(city_data.loc[3420020,:])
print("job",job_sums.loc[3420020])
print("+ec",pos_economic_sums.loc[3420020])
print("-ec",neg_economic_sums.loc[3420020])
print("food",food_sums.loc[3420020])
print("transit",transit_sums.loc[3420020])
print("housing",housing_sums.loc[3420020])
print("education",education_sums.loc[3420020])
print("diversity",diversity_sums.loc[3420020])
