'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
for each city that we are considering, we include the counties it is
associated with
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import pandas as pd
from collections import defaultdict

locs = pd.read_csv("popfiltered.csv")
cc_map = pd.read_csv("cities_counties.csv")
# each city maps to a list of counties
keys = zip(cc_map.city.values,cc_map.state_name.values)
cc_list = zip(keys, cc_map.county_fips.values)
cc_dict = defaultdict(list) # each key has a list
for k,v in cc_list:
    cc_dict[k].append(v)

def get_counties(row):
    breakers = ["CDP", "city", "town", "village", "County", "urban",
        "county", "municipality", "borough"]
    label = row['p_GEO.display-label']

    if ';' in label:
        tokens = label.split('; ')
        state = tokens[1]
        region = tokens[0].split(' ')[0]
    else:
        tokens = label.split(', ')
        state = tokens[1]
        tokens_reg = tokens[0].split(' ')
        region = ""
        for r in tokens_reg:
            if r in breakers:
                break
            if r == "St.":
                r = "Saint"
            if r == "Ste.":
                r = "Sainte"
            region += r + " "
        region = region[:-1] # take off last space
        tup = (region, state)
        if tup in cc_dict:
            return cc_dict[tup]
        if region == "Urban Honolulu":
            region = "Honolulu"
            tup = (region, state)
            if tup in cc_dict:
                return cc_dict[tup]
        if region[:-5] == " City":
            tup = (region[:-5], state)
            if tup in cc_dict:
                return cc_dict[tup]
        if region[:-5] == " Town":
            tup = (region[:-5, state])
            if tup in cc_dict:
                return cc_dict[tup]
        if '\'' in region:
            region = region.replace('\'','')
            tup = (region, state)
            if tup in cc_dict:
                return cc_dict[tup]
        if '-' in region:
            ind = region.find('-')
            tup = (region[:ind], state)
            if tup in cc_dict: # former
                return cc_dict[tup]
            tup = (region[ind+1:], state)
            if tup in cc_dict: # latter
                return cc_dict[tup]
        if '/' in region:
            ind = region.find('/')
            tup = (region[:ind], state)
            if tup in cc_dict: # former
                return cc_dict[tup]
            tup = (region[ind+1:], state)
            if tup in cc_dict: # latter
                return cc_dict[tup]
        # result
        print("Bad: ", label)
        return [] # empty list

county_fips = locs.apply(get_counties, axis=1)
locs["county_fips"] = county_fips
locs.to_csv("locs_with_county.csv")
