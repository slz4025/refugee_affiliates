# -*- coding: utf-8 -*-

import pandas as pd, numpy as np, statsmodels.api as sm
import matplotlib.pyplot as plt, matplotlib.cm as cm, matplotlib.font_manager as fm
from scipy.stats import pearsonr, ttest_rel
import nominatim
import requests
import time
import multiprocessing as mp
from sklearn.cluster import MeanShift
import numpy as np
import itertools
import math

pd.options.mode.chained_assignment = None

# function to convert string to float and handle empty string as NaN
def to_float(string_value):
    if (isinstance(string_value,float)):
      return string_value
    string_value = string_value.strip()
    return np.float(string_value) if string_value else np.nan

converters = {'rent':to_float, 
              'bedrooms':to_float, 
              'sqft':to_float, 
              'longitude':to_float, 
              'latitude':to_float}
'''
print("Opening filtered data")
reg_rent = pd.read_csv('data/usa-filt.csv', converters=converters) 

def city_tops(df):
    ext = df[['longitude','latitude','region']].values.tolist()
    ll = [e[0:2] for e in ext]
    X = np.array(ll)
    clustering = MeanShift().fit(X) # bandwidth=2
    identifier = df.iloc[0]['subdomain'] # unique key of group
    labels = [identifier + "_" + str(l) for l in clustering.labels_]
    df['cluster_label'] = labels
    groups = df.groupby(['cluster_label'])
    regs = [groups.get_group(g) for g in groups.groups]
    return regs

# sort by state then region
print("Grouping rows that are from same state and region")
reg_rent.set_index('pid')
reg_rent = reg_rent.sort_values(['state', 'region'])
groups = reg_rent.groupby(['state', 'region'])
state_regions = [groups.get_group(g) for g in groups.groups]
print("Dividing groups by subregion")
reg_srs = [city_tops(sr) for sr in state_regions]
reg_rents = [r for rs in reg_srs for r in rs] # flatten
reg_rents = pd.concat(reg_rents) # turn into one df
print("Unique subregions: ",reg_rents['cluster_label'].nunique())

# save
print("Saving subregion data")
with open('data/usa-subreg.csv', 'w') as f:
  reg_rents.to_csv(f, header=True)
'''

# open
print("Opening subregion data")
reg_rents = pd.read_csv('data/usa-subreg.csv', converters=converters) 
groups = reg_rents.groupby(['cluster_label'])
reg_rents = [groups.get_group(g) for g in groups.groups]

def rev_geo(row):
  query = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&" \
    + "lat=" + str(row['latitude']) \
    + "&lon=" + str(row['longitude']) \
    + "&zoom=18&addressdetails=1"
  resp = requests.get(url=query)
  try:
    data = resp.json()
    data = data['address']
    state = data['state']
    if 'city' in data:
        return (data['city'], state)
    elif 'county' in data:
        return (data['county'], state)
    else:
        print("Error: ", data)
  except:
    print("Error: ", resp.content)
    
def region_fix(region):
    if region == "LA":
        return "Los Angeles"
    elif region == "NYC":
        return "New York"
    elif region == "ABQ":
        return "Albuquerque"
    elif region == "SF":
        return "San Francisco"
    elif region == "PGH":
        return "Pittsburgh"
    elif "City of " in region:
        return region[8:] 
    else:
        return region

pop_name = 'data/ACS_17_5YR_DP05_with_ann.csv'
#population_df = pd.read_csv(pop_name, encoding='iso-8859-1') #, header=[0,1])
locs = pd.read_csv("data/locations.csv")

begin = time.time()
count = 1379

print("Starting to reverse_geocode and extract geoid")
for reg_rent in reg_rents[1378:]: #TODO
  print(count)
  # only apply geocoding on first
  row = reg_rent.iloc[0] # first
  results = rev_geo(row) # reg_rent.apply(rev_geo, axis=1)
  # state = row['state']
  try:
    region,state = results
    region = region_fix(region)
  except:
    # null
    region = ""
    state = ""
  num = reg_rent['pid'].count()
  regions = [region] * num # make results appropriate length
  states = [state] * num
  reg_rent['region2'] = regions
  reg_rent['state2'] = states
  reg_rent['geoid'] = [""] * num
  # put in geoid
  if not ("County" in region):
      first_pass = locs[locs['GEO.display-label'].str.match(region)]
      second_pass = first_pass[first_pass['GEO.display-label'].str.contains(state)]
      try:
          geoid = second_pass.iloc[0]['GEO.id2']
          geoids = [geoid] * num 
          reg_rent['geoid'] = geoids
      except:
          print("No matches: ", region, state)

  time.sleep(1)
  # write out each bit piece by piece
  if count == 0:
    with open('data/usa-loc.csv', 'w') as f:
      reg_rent.to_csv(f, header=True)
  else:
    with open('data/usa-loc.csv', 'a') as f:
      reg_rent.to_csv(f, header=False)
  count += 1

end = time.time()
print("Time: ", end-begin)

# repoen csv
print("Opening and preprocessing geoid-file")
converters = {'rent':to_float, 
              'bedrooms':to_float, 
              'sqft':to_float, 
              'longitude':to_float, 
              'latitude':to_float}
with_loc = pd.read_csv('data/usa-loc.csv', converters=converters) 
# remove all rows with no geo-code
region2_is_null = list(with_loc['region2'].isnull())
state2_is_null = list(with_loc['state2'].isnull())
geoid_is_null = list(with_loc['geoid'].isnull())
region2_remove = np.array(region2_is_null).nonzero()[0].tolist()
state2_remove = np.array(state2_is_null).nonzero()[0].tolist()
geoid_remove = np.array(geoid_is_null).nonzero()[0].tolist()
# rows_remove = np.array(some_null).nonzero()[0].tolist()
rows_remove = list(set(region2_remove + state2_remove + geoid_remove))
with_loc.drop(rows_remove, inplace=True)

print("Number of rows with geoid: ", with_loc['pid'].count())
print("Number of unique geoids: ", with_loc['geoid'].nunique())

# using minimum wage from 2018, for each state (and federal if no state min. wage)
# to be conservative, we look at the lowest min wage

converters = {'state':str, 'min_wage':float}
min_wage_pd = pd.read_csv('data/minimum_wage.csv', converters=converters)
min_wages_map = pd.Series(min_wage_pd.min_wage.values, \
                          index=min_wage_pd.state).to_dict()

def get_min_wage(row):
    return min_wages_map[row['state2']]

print("Calculating affordability statistic")
per_inc_housing = 0.5 # up-in-the-air, percentage of monthly income for housing
mw_upper_threshold = 1.75 # $12 wage (Leslie) vs. $7.25 min wage (in Pittsburgh) 
tax_consideration = 1 # amount left after tax
fact = per_inc_housing * mw_upper_threshold * tax_consideration
with_loc['min_wage'] = with_loc.apply(get_min_wage, axis=1)
# 8 hours a day, 20 workdays as a standard lower limit
with_loc['mw_monthly_amount'] = 8*20*with_loc['min_wage']
with_loc['affordable'] = with_loc['rent'] <= fact * with_loc['mw_monthly_amount']
#aff = with_loc[with_loc['below_threshold']==True]
#af_count = aff['below_threshold'].count()
#af_ratio = float(af_count) / float(with_loc['below_threshold'].count())
#print("Number of Affordable:\t{}\nRatio of Affordable:\t{}\n".format(af_count, af_ratio))

print("Affordability by geoid group")
# now determine for each locality, how many acc. affordable housing options there are
locality_groups = with_loc.groupby('geoid')
localities = [locality_groups.get_group(g) for g in locality_groups.groups]
affordable_count = [(l['geoid'].iloc[0],sum(l['affordable'].values)) for l in localities]
geoid_aff = pd.DataFrame(affordable_count, columns=['GEO.id2','affordable'])

print("Merging dataframes")
# left join, will definitely keep rows from locs but not nec. rows from geoid_aff
alocs = locs.set_index('GEO.id2').join(geoid_aff.set_index('GEO.id2'))

print("Saving affordable housing data by location")
with open('data/usa-aff.csv', 'w') as f:
  alocs.to_csv(f, header=True)


'''
# break out the proportion of listings below FMR, by bedrooms (agnostic to region)
reg_rent_below = reg_rent[reg_rent['below_fmr']]
below_FMR_br = reg_rent_below.groupby(['region', 'bedrooms']).count()['below_fmr'].unstack().sum()
total_br = reg_rent.groupby(['region', 'bedrooms']).count()['below_fmr'].unstack().sum()
fmr_ratio_by_br = below_FMR_br / total_br
fmr_ratio_by_br.index = [int(label) for label in fmr_ratio_by_br.index]
fmr_ratio_by_br.loc['all_1-4'] = fmr_ratio
fmr_ratio_by_br.name = 'total'
fmr_ratio_by_br

# Broken out by number of bedrooms, 29% of the 1 bedroom listings are below FMR, 36% of the 2 bedrooms, 51% of the 3 bedrooms, and 45% of the 4 bedrooms.

# break out the proportion of listings below FMR, by region
reg_rent_below = reg_rent[reg_rent['below_fmr']]
ratio_below_fmr = reg_rent_below.groupby('region').count()['below_fmr'] / reg_rent.groupby('region').count()['below_fmr']
ratio_below_fmr.name = 'all_1-4'

# break out the proportion of listings below FMR, by region and bedrooms
ratio_below_fmr_br = reg_rent_below.groupby(['region','bedrooms']).count()['below_fmr'] / reg_rent.groupby(['region','bedrooms']).count()['below_fmr']
ratio_below_fmr_br = ratio_below_fmr_br.unstack()
ratio_below_fmr_br.columns = [int(label) for label in ratio_below_fmr_br.columns]
ratio_below_fmr_br = pd.concat([ratio_below_fmr_br, ratio_below_fmr], axis=1)
ratio_below_fmr_br.head(6)

# The proportion of listings at/below the FMR varies considerably by region and by number of bedrooms.

# add the totals to the bottom of the dataframe, round it, and save to csv
ratio_below_fmr_br = ratio_below_fmr_br.append(fmr_ratio_by_br)
np.round(ratio_below_fmr_br, 2).to_csv('data/regions_fmr_summary.csv')

# plot the proportion of listings at/below FMR for the 15 most populous metros
countdata = ratio_below_fmr_br['all_1-4'][most_populous_regions.index].sort_values(ascending=False, inplace=False)
countdata = countdata.drop(labels='dallas', axis=0)
xlabels = [regions_full_names[x] for x in countdata.index]
ax = countdata.plot(kind='bar',                 
                    figsize=[9, 6], 
                    width=0.8, 
                    alpha=0.7, 
                    color='#003399',
                    edgecolor='w',
                    ylim=[0, 0.8],
                    grid=False)

ax.yaxis.grid(True)
ax.set_xticks(range(0, len(countdata)))
ax.set_xticklabels(xlabels, rotation=40, rotation_mode='anchor', ha='right', fontproperties=ticks_font)
for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
ax.set_title('Most populous metros, by proportion of listings below fair market rent', y=1.01, fontproperties=title_font)
ax.set_xlabel('', fontproperties=label_font)
ax.set_ylabel('Proportion of listings', fontproperties=label_font)

# draw a line showing the rent burden
plt.plot([-1, 60], [0.4, 0.4], 'k-', color='k', alpha=1, linewidth=1)

save_fig(plt.gcf(), 'fmr_proportions.png')
plt.show()

# The 14 most populous metro areas (i.e. the 15, sans Dallas, for whom there is no metro-level FMR data) by proportion of listings in the filtered data set at or below the HUD fair market rent value. The horizontal line marks the 40th percentile: for reference, HUD bases their FMRs on the 40th percentile rent.
# While regions like Phoenix, Atlanta, and Detroit have greater than 60% of their listings below the fair market rent, New York and Boston have single digit percentages of listings below the fair market rent.

## Validate the data set against HUD median rents by region

# get median rent per metro per # of bedrooms (1-4)
mask = filtered_listings['region'].isin(regions.sort_index(inplace=False).index) & filtered_listings['bedrooms'].isin([1,2,3,4])
region_br_rent = filtered_listings[mask].groupby(['region', 'bedrooms'])['rent'].median().unstack()
region_br_rent.columns = ['clist_{0}'.format(br) for br in pd.Series(region_br_rent.columns).astype(int)]

region_br_rent.head()

# join the Craigslist median rents and the HUD median rents
region_hud = pd.concat([region_br_rent, hud], axis=1)

# To assess the relationship between the Craigslist median rents and the HUD median rents (by region), first scatter plot them. HUD median rents are calculated for "fair market rent areas" that with a few exceptions generally correspond to OMB definitions of metropolitan areas, as these generally correspond well to housing market areas. However, these are median rent values, not FMRs here.

fig, ax = plt.subplots()
fig.set_size_inches(7, 7)

labels = ['1 br', '2 br', '3 br', '4 br']
plots = []
plots.append(ax.scatter(x=region_hud['HUD_median_1'], y=region_hud['clist_1'], c='g', edgecolor='k', alpha=.4, s=50))
plots.append(ax.scatter(x=region_hud['HUD_median_2'], y=region_hud['clist_2'], c='b', edgecolor='k', alpha=.4, s=50))
plots.append(ax.scatter(x=region_hud['HUD_median_3'], y=region_hud['clist_3'], c='m', edgecolor='k', alpha=.4, s=50))
plots.append(ax.scatter(x=region_hud['HUD_median_4'], y=region_hud['clist_4'], c='orange', edgecolor='k', alpha=.4, s=50))

ax.set_xlim([0,4100])
ax.set_ylim([0,4100])

ax.set_title('Craigslist median rent vs HUD median rent, by metro area', fontproperties=title_font)
ax.set_xlabel('HUD median rent by metro area (USD)', fontproperties=label_font)
ax.set_ylabel('Craigslist median rent by metro area (USD)', fontproperties=label_font)
plt.legend(plots, labels, loc=4, prop=ticks_font)

# draw a line indicating a perfect linear relationship
plt.plot([0, 4100], [0, 4100], 'k-', color='k', alpha=0.2, linewidth=1.5)

save_fig(plt.gcf(), 'median_rent_hud_craigslist.png')
plt.show()

# Points are above the line when Craigslist median rent is greater than HUD median rent, below the line when HUD median rent is greater than Craigslist median rent, and on the line when the two median rents are equal.

# plot same data, but with simple bivariate regression lines
fig, ax = plt.subplots()
fig.set_size_inches(7, 7)
bedrooms = [1, 2, 3, 4]
labels = ['1 br', '2 br', '3 br', '4 br']
color_list = get_colors('YlOrRd', n=len(labels), start=0.25, stop=0.95)
plots = []

for br, c in zip(bedrooms, color_list):
    
    # regress craigslist data on HUD data
    X = region_hud['HUD_median_{}'.format(br)]
    Y = region_hud['clist_{}'.format(br)]
    results = sm.OLS(Y, sm.add_constant(X)).fit()
    
    # calculate estimated y values for regression line
    X_line = pd.Series(X)
    X_line.loc[0] = 0
    X_line.loc[4100] = 4100
    Y_est = X_line * results.params[1] + results.params[0]
    
    # draw points and regression line
    plots.append(ax.scatter(X, Y, c=c, edgecolor='#333333', alpha=0.8, s=40, zorder=2))
    ax.plot(X_line, Y_est, c=c, alpha=0.5, linewidth=2, zorder=1)

ax.set_xlim([0,4100])
ax.set_ylim([0,4100])

ax.set_title('Craigslist median rent vs HUD median rent, by metro area', fontproperties=title_font)
ax.set_xlabel('HUD median rent by metro area (USD)', fontproperties=label_font)
ax.set_ylabel('Craigslist median rent by metro area (USD)', fontproperties=label_font)
plt.legend(plots, labels, loc=4, prop=ticks_font)

save_fig(plt.gcf(), 'median_rent_hud_craigslist_regression.png')
plt.show()

# now get the correlation coefficient and statistical significance for each number of bedrooms
N = len(region_hud)
for br in [1, 2, 3, 4]:
    r, p = pearsonr(region_hud['clist_{}'.format(br)], region_hud['HUD_median_{}'.format(br)])
    r_square = r ** 2
    t = r * (np.sqrt((N - 2)/(1 - r_square)))
    
    print('{} br:'.format(br), 'r={:0.2f},'.format(r), 'r-square={:.2f},'.format(r_square),)
    print('t={:05.2f},'.format(t), 'df={},'.format(N-2), 'p={:0.23f}'.format(p))

# The correlations between HUD and Craigslist median rents are positive, strong, and statistically significant (p<.0001). The coefficient of determinations (r<sup>2</sup>) reveal that 83%, 81%, 77%, and 63% (for 1, 2, 3, and 4 bedroom listings, respectively) of the variation in Craigslist median rents (per region) can be explained by HUD median rents.
# Now perform a dependent samples t-test for each number of bedrooms to compare the Craigslist and HUD means (of median rents by region) to see if they are significantly different from each other.

# dependent samples t-test to see if means are significantly different
for br in [1, 2, 3, 4]:
    t, p = ttest_rel(region_hud['clist_{}'.format(br)], region_hud['HUD_median_{}'.format(br)])
    print(br, 'br:', 't={},'.format(round(t, 2)), 'p={}'.format(round(p, 3)))

# The null hypothesis H<sub>0</sub> is that the means are the same. We can reject the null for 1 br (p<.01) and 3 br (p<.02), indicating that the means of Craigslist and HUD are statistically significantly different. We cannot reject the null for 2 br (p=.07) or 4 br (p=.69), indicating that the means of Craigslist and HUD are not statistically significantly different (ie, we would expect a t-statistic of this size 7% and 69% of the time when there is no real difference between the population means).
# Two-sample t-tests require that a set of conditions be met. First, each sample must be simple random sampling - ours aren't exactly that. Second, the sampling distribution should be normal - ie, symmetric, unskewed, and without outliers. None of these samples are normally distributed - that's to be expected with real world data. But most of these samples are considerably positively skewed by outliers, so the t-test may not really be appropriate here.
# Instead, let's try to get at the degree and direction of bias of Craigslist median rents with regards to HUD median rents by examining ratios.

# now calculate the ratio of median rents in filtered data set (per region and per # of bedrooms) to HUD median rents
region_hud['hud_ratio_1'] = region_hud['clist_1'] / region_hud['HUD_median_1']
region_hud['hud_ratio_2'] = region_hud['clist_2'] / region_hud['HUD_median_2']
region_hud['hud_ratio_3'] = region_hud['clist_3'] / region_hud['HUD_median_3']
region_hud['hud_ratio_4'] = region_hud['clist_4'] / region_hud['HUD_median_4']

region_hud_means = region_hud[['hud_ratio_1','hud_ratio_2','hud_ratio_3','hud_ratio_4']].mean()
region_hud_means

# On average (arithmetic mean) in these regions, median rents in the filtered data set are 7.5% higher for 1 bedroom, 3.2% higher for 2 bedrooms, 7.2% lower for 3 bedrooms, and 1.2% higher for 4 bedrooms than the HUD 2014 median rent.

# add the mean values to the bottom then format all the ratios as +/- percentages
region_hud_means.name='means'
region_hud = region_hud.append(region_hud_means)
cols = ['hud_ratio_1','hud_ratio_2','hud_ratio_3','hud_ratio_4']
region_hud[cols] = region_hud[cols].applymap(lambda x: round(x, 2)).values
region_hud[cols].tail()

# save to csv and remove the means row
region_hud.to_csv('data/regions_hud_summary.csv')
region_hud = region_hud.drop(labels='means', axis=0)

## Next, analyze listings counts and median rent per sq ft, by day of the week

days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# how many times does each day of the week appear in the data set of filtered listings
listings_per_day = filtered_listings.groupby('day_of_week').size()
listings_per_day.index = days_of_the_week
listings_per_day

# how many times does each day of the week appear in the data set of filtered listings
listings_per_date = pd.DataFrame(filtered_listings['date'].value_counts())
listings_per_date['day_of_week'] = listings_per_date.index.weekday
day_counts = listings_per_date['day_of_week'].value_counts().sort_index()
day_counts.index = days_of_the_week
day_counts

# how many filtered listings per day of the week normalized by how many times that day appears in the data set
avg_listings_per_day = listings_per_day / day_counts
avg_listings_per_day.name = 'avg_count_filtered'

# what is the median rent per day of the week
median_rent_per_day = filtered_listings.groupby('day_of_week')['rent_sqft'].median().sort_index()
median_rent_per_day.index = days_of_the_week
median_rent_per_day.name = 'median_rent_filtered'

# display a summary of the filtered data set, by day of the week
day_summaries = pd.concat(objs=[avg_listings_per_day, median_rent_per_day], axis=1)
day_summaries

# The average number of listings posted and the median rent per square foot, per day of the week (filtered data set)

# for comparison, create the same dataframe above, but for the original thorough set of listings
all_listings_per_day = all_listings.groupby(all_listings['day_of_week']).size()
all_listings_per_day.index = days_of_the_week
all_listings_per_date = pd.DataFrame(all_listings['date'].value_counts())
all_listings_per_date['day_of_week'] = all_listings_per_date.index.weekday
all_day_counts = all_listings_per_date['day_of_week'].value_counts().sort_index()
all_day_counts.index = days_of_the_week
all_avg_listings_per_day = all_listings_per_day / all_day_counts
all_avg_listings_per_day.name = 'avg_count_original'
all_median_rent_per_day = all_listings.groupby(all_listings['day_of_week'])['rent_sqft'].median().sort_index()
all_median_rent_per_day.index = days_of_the_week
all_median_rent_per_day.name = 'median_rent_original'
all_day_summaries = pd.concat(objs=[all_avg_listings_per_day, all_median_rent_per_day], axis=1)

# compare the daily summaries from the original thorough data set, to those of the filtered set
combined_summaries = pd.concat(objs=[day_summaries, all_day_summaries], axis=1)
combined_summaries['count_ratio'] = combined_summaries['avg_count_filtered'] / combined_summaries['avg_count_original']
combined_summaries['rent_ratio'] = combined_summaries['median_rent_filtered'] / combined_summaries['median_rent_original']
combined_summaries = combined_summaries.reindex(columns=['avg_count_filtered','avg_count_original','count_ratio',
                                                         'median_rent_filtered','median_rent_original','rent_ratio'])
combined_summaries

# The average number of listings posted and the median rent per square foot, by day of the week, for the original thorough data set and the filtered data set. Ratios show the ratio of the filtered set's value to the original set's value.
# Tuesdays have a noticeably higher ratio of unique, reasonable rental listings posted compared to Mondays. Explore that further, below.

# for more comparison, create the same dataframe as earlier, but for the unique set of listings, pre-filter
unique_listings_per_day = unique_listings.groupby(unique_listings['day_of_week']).size()
unique_listings_per_day.index = days_of_the_week
unique_listings_per_date = pd.DataFrame(unique_listings['date'].value_counts())
unique_listings_per_date['day_of_week'] = unique_listings_per_date.index.weekday
unique_day_counts = unique_listings_per_date['day_of_week'].value_counts().sort_index()
unique_day_counts.index = days_of_the_week
unique_avg_listings_per_day = unique_listings_per_day / unique_day_counts
unique_avg_listings_per_day.name = 'avg_count_unique'
unique_median_rent_per_day = unique_listings.groupby(unique_listings['day_of_week'])['rent_sqft'].median().sort_index()
unique_median_rent_per_day.index = days_of_the_week
unique_median_rent_per_day.name = 'median_rent_unique'
unique_day_summaries = pd.concat(objs=[unique_avg_listings_per_day, unique_median_rent_per_day], axis=1)

# look at the ratios (original, unique, and filtered) side by side
all_ratios = combined_summaries['avg_count_original'] / combined_summaries['avg_count_original'].sum()
unique_ratios = unique_day_summaries['avg_count_unique'] / unique_day_summaries['avg_count_unique'].sum()
filtered_ratios = combined_summaries['avg_count_filtered'] / combined_summaries['avg_count_filtered'].sum()

avg_count_ratios = pd.concat(objs=[all_ratios, unique_ratios, filtered_ratios], axis=1)
avg_count_ratios = avg_count_ratios.rename(columns={'avg_count_original':'original', 
                                                    'avg_count_unique':'unique', 
                                                    'avg_count_filtered':'filtered'})
avg_count_ratios

# plot the ratios of rental listings (original, unique, and filtered) by day of week
countdata = avg_count_ratios
ax = countdata.plot(kind='bar',                 
                    figsize=[8, 6], 
                    ylim=[0,.2],
                    width=0.6, 
                    alpha=0.5,
                    color=['r','b','g'],
                    edgecolor='gray',
                    grid=False)

ax.yaxis.grid(True)
ax.set_xticks(map(lambda x: x, range(0, len(countdata))))
ax.set_xticklabels(countdata.index, rotation=35, rotation_mode='anchor', ha='right', fontproperties=ticks_font)
for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
ax.set_title('Each day of the week\'s ratio of total rental listings posted', fontproperties=title_font)
ax.set_xlabel('', fontproperties=label_font)
ax.set_ylabel('Ratio of listings posted per day', fontproperties=label_font)

save_fig(plt.gcf(), 'day_of_week_ratio_listings_posted.png')
plt.show()

# Here it is easy to see that Mondays account for a greater proportion of posted rental listings before we filter the data set for duplicates/re-posts and reasonable values. In contrast, Tuesdays account for a greater proportion of the listings after we filter the data set. It seems that Mondays suffer from more low quality postings, and Tuesdays have a greater ratio of high quality postings.

# plot the avg number of filtered rental listings, by day of week
countdata = avg_listings_per_day
ax = countdata.plot(kind='bar',                 
                    figsize=[8, 6], 
                    width=0.6, 
                    alpha=0.6,
                    color='g',
                    edgecolor='gray',
                    grid=False)

ax.yaxis.grid(True)
ax.set_xticks(map(lambda x: x, range(0, len(countdata))))
ax.set_xticklabels(countdata.index, rotation=35, rotation_mode='anchor', ha='right', fontproperties=ticks_font)
for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
ax.set_title('Filtered rental listings posted, by day of the week', fontproperties=title_font)
ax.set_xlabel('', fontproperties=label_font)
ax.set_ylabel('Mean listings posted per day', fontproperties=label_font)

save_fig(plt.gcf(), 'day_of_week_listings_count_posted_filtered.png')
plt.show()

# Sundays see only half as many (filtered) listings posted as Mondays and Tuesdays do.
## Now look at median rent/sqft by day of the week

# look at the median rent/sqft (original, unique, and filtered) side by side
all_rent = combined_summaries['median_rent_original']
unique_rent = unique_day_summaries['median_rent_unique']
filtered_rent = combined_summaries['median_rent_filtered']

median_rents = pd.concat(objs=[all_rent, unique_rent, filtered_rent], axis=1)
median_rents = median_rents.rename(columns={'median_rent_original':'original', 
                                                    'median_rent_unique':'unique', 
                                                    'median_rent_filtered':'filtered'})
median_rents

# plot the median rent/sqft (original, unique, and filtered) by day of week
countdata = median_rents
ax = countdata.plot(kind='bar',                 
                    figsize=[8, 6], 
                    ylim=[0, 1.4],
                    width=0.6, 
                    alpha=0.5,
                    color=['r','b','g'],
                    edgecolor='gray',
                    grid=False)

ax.yaxis.grid(True)
ax.set_xticks(map(lambda x: x, range(0, len(countdata))))
ax.set_xticklabels(countdata.index, rotation=35, rotation_mode='anchor', ha='right', fontproperties=ticks_font)
for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
ax.set_title('Median rent per square foot, by day of the week posted', fontproperties=title_font)
ax.set_xlabel('', fontproperties=label_font)
ax.set_ylabel('Median rent per square foot (USD)', fontproperties=label_font)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper left')

save_fig(plt.gcf(), 'day_of_week_median_rent_sqft.png')
plt.show()

# plot the median rent per sq ft by day of the week for the filtered data set only
countdata = median_rent_per_day
ax = countdata.plot(kind='bar',                 
                    figsize=[8, 6], 
                    width=0.6, 
                    alpha=0.7,
                    color='g',
                    edgecolor='gray',
                    grid=False,
                    ylim=[0, 1.4])

ax.yaxis.grid(True)
ax.set_xticks(map(lambda x: x, range(0, len(countdata))))
ax.set_xticklabels(countdata.index, rotation=35, rotation_mode='anchor', ha='right', fontproperties=ticks_font)
for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
ax.set_title('Median rent per square foot, by day of the week', fontproperties=title_font)
ax.set_xlabel('', fontproperties=label_font)
ax.set_ylabel('Median rent per square foot (USD)', fontproperties=label_font)

save_fig(plt.gcf(), 'day_of_week_median_rent_sqft_filtered.png')
plt.show()

# Median rents are about 11.5% higher on Sundays (the most expensive day) than they are on Wednesdays (the least expensive day)
## Retain only the rows with lat-long data, then show descriptive stats for the different stages of the data set

# clean data further by only retaining rows with lat-long data
geolocated_filtered_listings = pd.DataFrame(filtered_listings)
geolocated_filtered_listings = geolocated_filtered_listings[pd.notnull(geolocated_filtered_listings['latitude'])]
geolocated_filtered_listings = geolocated_filtered_listings[pd.notnull(geolocated_filtered_listings['longitude'])]

print(len(geolocated_filtered_listings))
print(len(geolocated_filtered_listings) / float(len(filtered_listings)))

# There are 1,456,338 geolocated listings in the filtered data set.
# To recap:
# - There were 10,958,372 rental listings in the original, full data set.
# - Of those total listings, 5,480,435 or 50.0% were unique.
# - Of those unique listings, 2,947,761 or 53.8% had rent, sqft, and reasonable values.
# - Of those filtered listings, 1,456,338 or 49.4% were geolocated.
# Interestingly, each filtering step retained almost exactly half of the remaining data set.

# how many regions are in the data set?
print(len(all_listings['region'].unique()))
print(len(filtered_listings['region'].unique()))

print(len(all_listings))
all_listings.describe()

print(len(unique_listings))
unique_listings.describe()

print(len(thorough_listings))
thorough_listings.describe()

print(len(filtered_listings))
filtered_listings.describe()

print(len(geolocated_filtered_listings))
geolocated_filtered_listings.describe()

## Finally, save the geolocated filtered data to CSV for GIS mapping

# only retain the relevant columns, then save the dataframe to csv
cols = ['pid', 'date', 'region', 'neighborhood', 'rent', 'bedrooms', 'sqft', 'rent_sqft', 
        'rent_sqft_cat', 'longitude', 'latitude']
data_output = geolocated_filtered_listings[cols]
data_output.to_csv('data/geolocated_filtered_listings.csv', index=False)

# also save a minimized csv with only category, lat, and long
min_cols = ['rent_sqft_cat', 'longitude', 'latitude']
data_output_min = geolocated_filtered_listings[min_cols]
data_output_min.to_csv('data/geolocated_filtered_listings_min.csv', index=False)
'''
