'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
For each city, we map it to its associated food information using
the intermediate county.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import pandas as pd
import numpy as np

stores = pd.read_csv("food_access_stores.csv")
local = pd.read_csv("food_access_local.csv")
indices = ["FIPS","State","County"]
access = pd.merge(stores, local, how="inner", on=indices)

X = ["FIPS", "State", "County", "SNAPSPTH16", \
        "FMRKTPTH16", "PCT_FMRKT_SNAP16", "PCT_FMRKT_WIC16",\
        "PCT_FMRKT_WICCASH16", "PCT_FMRKT_SFMNP16"]
access = access[X]

cc_fips = pd.read_csv("locs_with_county.csv")

def get_vars(row):
    county_fips = row["county_fips"]
    county_fips = county_fips[1:-1]
    county_fips = county_fips.split(", ")
    good_rows = access[access["FIPS"].isin(county_fips)]
    if len(good_rows) == 0:
        return tuple([""] * 10)
    good_row = good_rows.iloc[0] # only one
    # filter out bad
    stores_snap = good_row["SNAPSPTH16"]
    farm_market = good_row["FMRKTPTH16"]
    pct_snap_m = good_row["PCT_FMRKT_SNAP16"] / 100.0
    pct_wic_m = good_row["PCT_FMRKT_WIC16"] / 100.0
    pct_wicc_m = good_row["PCT_FMRKT_WICCASH16"] / 100.0
    pct_sfmnp_m = good_row["PCT_FMRKT_SFMNP16"] / 100.0
    qua_snap_m = "" 
    qua_wic_m = ""
    qua_wicc_m = ""
    qua_sfmnp_m = ""
    if np.isnan(stores_snap):
        stores_snap = ""
    if np.isnan(farm_market):
        farm_market = ""
    else:
        if np.isnan(pct_snap_m):
            pct_snap_m = ""
        else:
            qua_snap_m = pct_snap_m * farm_market
        if np.isnan(pct_wic_m):
            pct_wic_m = ""
        else:
            qua_wic_m = pct_wic_m * farm_market
        if np.isnan(pct_wicc_m):
            pct_wicc_m = ""
        else:
            qua_wicc_m = pct_wicc_m * farm_market
        if np.isnan(pct_sfmnp_m):
            pct_sfmnp_m = ""
        else:
            qua_sfmnp_m = pct_sfmnp_m * farm_market
    return (stores_snap, farm_market, \
            pct_snap_m, pct_wic_m, pct_wicc_m, pct_sfmnp_m, \
            qua_snap_m, qua_wic_m, qua_wicc_m, qua_sfmnp_m)

var = cc_fips.apply(get_vars, axis=1)
cc_fips["SNAPSPTH16"] = [v[0] for v in var]
cc_fips["FMRKTPTH16"] = [v[1] for v in var]
cc_fips["PCT_FMRKT_SNAP16"] = [v[2] for v in var]
cc_fips["PCT_FMRKT_WIC16"] = [v[3] for v in var]
cc_fips["PCT_FMRKT_WICCASH16"] = [v[4] for v in var]
cc_fips["PCT_FMRKT_SFMNP16"] = [v[5] for v in var]
cc_fips["QUA_FMRKT_SNAP16"] = [v[6] for v in var]
cc_fips["QUA_FMRKT_WIC16"] = [v[7] for v in var]
cc_fips["QUA_FMRKT_WICCASH16"] = [v[8] for v in var]
cc_fips["QUA_FMRKT_SFMNP16"] = [v[9] for v in var]

cc_fips.to_csv("cities_food.csv")
