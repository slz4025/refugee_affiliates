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
        urls_ = pd.read_csv("urls_filtered.csv")
        geoids = list(urls_['p_GEO.id2'])
        re_sts = list(urls_['p_GEO.display-label'])
        state = list(urls_['state'])
        region = list(urls_['region'])

        for i,r in urls_.iterrows():
            geoid = r['p_GEO.id2']
            re_sts = r['p_GEO.display-label']
            state = r['state']
            region = r['region']
            url = r['url']
            # apts / housing with filters
            try:
                ind = url.find('craigslist.org/')
            except:
                continue
            beg = url[:ind+15]
            apts = "d/apts_housing_for_rent/search/apa"
            splace = url[ind+15:] # rest
            crit = "&sort=date&hasPic=1&bundleDuplicates=1&min_price=100&max_price=1015&min_bedrooms=1&min_bathrooms=1&availabilityMode=0&laundry=1&laundry=4&laundry=2&laundry=3&sale_date=all+dates"
            use_url = beg + apts + splace + crit
            print("url",use_url)
            yield scrapy.Request(use_url, meta={'state':state,'region':region, \
                    'geoid':geoid, 'place':re_sts})

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
        return item
