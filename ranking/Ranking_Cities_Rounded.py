#!/usr/bin/env python
# coding: utf-8

## 
## Ranks cities according to normalized feature classes
## Takes min 
##

import numpy as np
import pandas as pd

# city features
city_data = pd.read_csv('./merged_city_data_normalized_with_employment.csv').set_index('GeoID')
city_data_with_names = pd.read_csv('./merged_city_data_normalized.tsv',
        sep='\t')
place_map = pd.Series(city_data_with_names['Place Name'].values,
        index=city_data_with_names['GeoID']).to_dict()
# affiliate cities and their geoids
aff_cities = pd.read_csv('./Affiliate-City-to-Id2.csv', names=['Place Name',
    'GeoID'])
aff_map = pd.Series(aff_cities['Place Name'].values,
    index=aff_cities['GeoID']).to_dict()

job_features = [
    'Indeed job count normalized min_max_normalized'
]

pos_economic_features = [
    'Employment to population ratio percentage min_max_normalized',
    'Employment Rate Prediction min_max_normalized'
]

neg_economic_features = [
    'Number of people below the poverty level normalized min_max_normalized',
    'Unemployment rate'
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
job_weight = 2 # high
pos_economic_weight = 1
neg_economic_weight = -1
food_weight = 1
transit_weight = 1
housing_weight = 2 # high
education_weight = 1
diversity_weight = 1

# normalize by size of each feature-class
job_mean = city_data[city_data.columns[\
        city_data.columns.isin(job_features)]].sum(axis=1)\
        / len(job_features)
pos_economic_mean = city_data[city_data.columns[\
        city_data.columns.isin(pos_economic_features)]].sum(axis=1)\
        / len(pos_economic_features)
# keep positive
neg_economic_mean = 1 - city_data[city_data.columns[\
        city_data.columns.isin(neg_economic_features)]].sum(axis=1)\
        / len(neg_economic_features)
food_mean = city_data[city_data.columns[\
        city_data.columns.isin(food_features)]].sum(axis=1)\
        / len(food_features)
transit_mean = city_data[city_data.columns[\
        city_data.columns.isin(transit_features)]].sum(axis=1)\
        / len(transit_features)
housing_mean = city_data[city_data.columns[\
        city_data.columns.isin(housing_features)]].sum(axis=1)\
        / len(housing_features)
education_mean = city_data[city_data.columns[\
        city_data.columns.isin(education_features)]].sum(axis=1)\
        / len(education_features)
diversity_mean = city_data[city_data.columns[\
        city_data.columns.isin(diversity_features)]].sum(axis=1)\
        / len(diversity_features)

# importance on features is done by taking powers
job_mean = job_mean.pow(2)
housing_mean = housing_mean.pow(2)

feature_classes = pd.concat([job_mean, pos_economic_mean,
    neg_economic_mean, food_mean, transit_mean, housing_mean,
    education_mean, diversity_mean], axis=1)
city_scores = feature_classes.min(axis=1)

city_scores.sort_values(ascending=False, inplace=True)

to_display = 10
for geoid, score in city_scores[:to_display].iteritems():
    print("Score: {:.2f}\tGeoID: {}\tPlace Name: {}\tAffiliate Status: {}"\
    .format(score, geoid, place_map[geoid], geoid in aff_map))
    print("job",job_mean.loc[geoid])
    print("+ec",pos_economic_mean.loc[geoid])
    print("-ec",neg_economic_mean.loc[geoid])
    print("food",food_mean.loc[geoid])
    print("transit",transit_mean.loc[geoid])
    print("housing",housing_mean.loc[geoid])
    print("education",education_mean.loc[geoid])
    print("diversity",diversity_mean.loc[geoid])
    print()

