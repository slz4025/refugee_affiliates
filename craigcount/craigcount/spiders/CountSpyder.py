# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html
from items import CountItem
import pandas as pd


class MySpider(scrapy.Spider): 
    name = "craig"
    allowed_domains = ["craigslist.org/"]

    def start_requests(self):
        min_wage_ = pd.read_csv("minimum_wage.csv")
        mw_map = pd.Series(min_wage_.min_wage.values,\
                index=min_wage_.state).to_dict()

        urls_ = pd.read_csv("urls_filtered.csv")

        for i,r in urls_.iterrows():
            geoid = r['p_GEO.id2']
            re_sts = r['p_GEO.display-label']
            state = r['state']
            region = r['region']
            url = r['url']
            min_wage = mw_map[state]
            per_inc_housing = 0.5 # up-in-the-air, percentage of monthly income
            mw_upper_threshold = 1.75 # $12 wage (Leslie) vs. $7.25 min wage
            tax_consideration = 1 # amount left after tax
            fact = per_inc_housing * mw_upper_threshold * tax_consideration
            up_bound = min_wage * 8 * 20 * fact # per month
            up_bound = int(up_bound)
            print("upperbound",up_bound)
            # apts / housing with filters
            try:
                ind = url.find('craigslist.org/')
            except:
                # make entry for those without craigslist
                item = CountItem()
                item['count'] = -1 # no count
                item['state'] = state 
                item['geoid'] = geoid
                item['region'] = region
                item['place'] = re_sts
                item['minwage'] = min_wage
                continue

            beg = url[:ind+15]
            apts = "d/apts_housing_for_rent/search/apa"
            splace = url[ind+15:] # rest
            # change upper bound
            crit = "&sort=date&hasPic=1&bundleDuplicates=1&min_price=100&max_price={}&min_bedrooms=1&min_bathrooms=1&availabilityMode=0&laundry=1&laundry=4&laundry=2&laundry=3&sale_date=all+dates".format(up_bound)
            use_url = beg + apts + splace + crit
            print("url",use_url)
            yield scrapy.Request(use_url, meta={'state':state,'region':region, \
                    'geoid':geoid, 'place':re_sts, 'minwage':min_wage})

    def parse(self, response):
        base = response.request.url
        item = CountItem()
        try:
            count_ = int(response.xpath(".//span[@class='totalcount']/text()").extract()[0])
            item['count'] = count_
        except:
            item['count'] = 0 # none
        item['state'] = response.meta['state']
        item['geoid'] = response.meta['geoid']
        item['region'] = response.meta['region']
        item['place'] = response.meta['place']
        item['minwage'] = response.meta['minwage']
        return item
