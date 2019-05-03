#!/usr/bin/env python
# coding: utf-8

## 
## Ranks cities according to normalized feature classes
## Maybe min/max => mean across class => mean/std of class for z-score
## also takes min 
##

import numpy as np
import pandas as pd

# city features
city_data = pd.read_csv('./merged_city_data_normalized_with_employment.csv')
place_map = pd.Series(city_data['Place Name'].values,
        index=city_data['GeoID']).to_dict()
city_data = city_data.set_index('GeoID')
# affiliate cities and their geoids
aff_cities = pd.read_csv('./Affiliate-City-to-Id2.csv', names=['Place Name',
    'GeoID'])
aff_map = pd.Series(aff_cities['Place Name'].values,
    index=aff_cities['GeoID']).to_dict()

job_features = [
    ('Indeed job count normalized', 1)
]

pos_economic_features = [
    ('Employment to population ratio percentage', 0.6),
    ('Employment Rate Prediction', 0.4)
]

neg_economic_features = [
    ('Number of people below the poverty level normalized', 0.6),
    ('Unemployment rate percentage', 0.4)
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
    ('Public transportation proportion', .8),
    ('Proportion of public transit to work under 30 minutes', .2)
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
neg_feature_names = [n[0] for n in neg_economic_features]
pos_feature_names = [p[0] for p in \
        set(all_features).difference(set(neg_feature_names))]

# turn nans in positive features to 0 (standard minimum) 
city_data[pos_feature_names] = city_data[pos_feature_names].fillna(0)
# turn nans in negative features to the maximum (the greater, the worse)
city_data[neg_feature_names] = city_data[neg_feature_names]\
        .fillna(city_data[neg_feature_names].max())

# compute z-score for each feature
for f,s in all_features:
    city_data[f+" z-score"] = (city_data[f] - city_data[f].mean())\
    / city_data[f].std()

# take weighted mean
for c in classes:
    city_data[c] = sum([s*city_data[f + " z-score"] for f,s in classes[c]])

# negate
city_data["- Economic features"] = -1 * city_data["- Economic features"]

# weighing, make more important features more likely to be the minimum
city_data["Job features"] -= 1#0.5
city_data["Housing features"] -= 1#0.5
city_data["Transit features"] -= 2#0.5
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
    for c in classes:
        print(c, city_data.loc[geoid][c])
    for f,s in all_features:
        print(f, city_data.loc[geoid][f])
    print()
