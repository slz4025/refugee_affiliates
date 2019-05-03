#!/usr/bin/env python
# coding: utf-8

## 
## Ranks cities according to normalized feature classes
## Maybe min/max => mean across class => mean/std of class for z-score
## also takes min 
##


import numpy as np
import pandas as pd


# In[43]:


# city features
#city_data = pd.read_csv('./merged_city_data_normalized_with_employment.csv').set_index('GeoID')
# incomplete dataset, but has place names
city_data = pd.read_csv('./merged_city_data_normalized.tsv',
        sep='\t')#.set_index('GeoID')
city_data = city_data.drop_duplicates()
place_map = pd.Series(city_data['Place Name'].values,
        index=city_data['GeoID']).to_dict()
city_data = city_data.set_index('GeoID')
# affiliate cities and their geoids
aff_cities = pd.read_csv('./Affiliate-City-to-Id2.csv', names=['Place Name',
    'GeoID']) #.set_index('GeoID')
aff_map = pd.Series(aff_cities['Place Name'].values,
    index=aff_cities['GeoID']).to_dict()

# TODO include population in ranking

job_features = [
    ('Indeed job count normalized', 1)
]

pos_economic_features = [
    ('Employment to population ratio percentage', 1)#,
    #('Employment Rate Prediction', 0.4)
]

neg_economic_features = [
    ('Number of people below the poverty level normalized', 0.6),
    ('Unemployment rate', 0.4)
]

food_features = [
    ('SNAP-authorized Stores per 1000 people (2016)', 0.4),
    ('Farmers Markets per 1000 people (2016)', 0.4),
    ('Farmer Markets with SNAP per 1000 people (2016)', 0.05),
    ('Farmer Markets with WIC per 1000 people (2016)', 0.05),
    ('Farmer Markets with WIC Cash per 1000 people (2016)', 0.05),
    ('Farmer Markets with SFMNP per 1000 people (2016)', 0.05)
]

transit_features = [
    ('Public transportation proportion', 0.85),
    ('Proportion of public transit to work under 30 minutes', 0.15)
]

housing_features = [
    ('Affordable housing in market normalized', 0.6),
    ('Craigslist affordable house count normalized', 0.4)
]

education_features = [
    ('Number of people with a bachelors degree or higher normalized',1)
]

diversity_features = [
    ('Simpsons diversity score',1),
]

# TODO
city_data['Affordable housing in market normalized'] = \
        city_data['Affordable housing in market'] / city_data['Population']

all_features = job_features + pos_economic_features + neg_economic_features\
        + food_features + transit_features + housing_features\
        + education_features + diversity_features
classes = {"Job features":job_features,\
           "+ Economic features":pos_economic_features,\
           "- Economic features":neg_economic_features,\
           "Food features":food_features,\
           "Transit features":transit_features,\
           "Housing features":housing_features,\
           "Education features":education_features,\
           "Diversity features":diversity_features}

# turn nans to 0 
# may cause issues with neg features!!!
city_data = city_data.fillna(0)

# compute z-score for each feature
for f,s in all_features:
    city_data[f+" z-score"] = (city_data[f] - city_data[f].mean())\
    / city_data[f].std()

# take weighted mean
for c in classes:
    city_data[c] = sum([s*city_data[f + " z-score"] for f,s in classes[c]])

# negate
city_data["- Economic features"] = -1 * city_data["- Economic features"]
        

# weighing
job_weight = 2 # high
pos_economic_weight = 1
neg_economic_weight = -1
food_weight = 1
transit_weight = 1
housing_weight = 2 # high
education_weight = 1
diversity_weight = 1

# how much more likely will housing and jobs be the minimum
city_data["Job features"] -= 0.5
city_data["Housing features"] -= 0.5
city_data["Transit features"] -= 0.5
city_data["Food features"] += 0.25
city_data["Education features"] += 0.25

# take minimum as score
class_names = list(classes.keys())
city_scores = city_data[class_names].min(axis=1)

city_scores.sort_values(ascending=False, inplace=True)

to_display = 10
for geoid, score in city_scores[:to_display].iteritems():
    print("Score: {:.2f}\tGeoID: {}\tPlace Name: {}\tAffiliate Status: {}"\
    .format(score, geoid, place_map[geoid], geoid in aff_map))
    #print(city_data.loc[geoid,:])
    for c in classes:
        print(c, city_data.loc[geoid][c])
    for f,s in all_features:
        print(f, city_data.loc[geoid][f])
    print()
