# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html
from items import IndeedItem
import pandas as pd


class MySpider(scrapy.Spider): 
    name = "indeed"
    allowed_domains = ["www.indeed.com"]

    def extract_loc(self, st):
        comma = st.find(',')
        state = st[comma+1:] # after space
        raw_region = st[:comma].split(' ')
        region = ""
        term = ['CDP', 'city', 'town', 'village', 'municipality', 'borough']
        for r in raw_region:
            if r in term:
                break
            region += r + " " # space
        # get rid of last space
        return (region[:-1], state)

    def start_requests(self):
        loc = pd.read_csv("locations.csv")
        geoids = list(loc['GEO.id2'])
        re_sts = list(loc['GEO.display-label'])
        re_sts = [self.extract_loc(e) for e in re_sts]
        re_sts = list(zip(geoids,re_sts))
        for e in re_sts:
            geoid, rs = e
            re, st = rs
            url = "https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&" \
                  + "as_not=&as_ttl=&as_cmp=&jt=fulltime&st=&as_src=&" \
                  + "salary=$14,500+-+$20,000&radius=25&l=" \
                  + re + ",+" + st \
                  + "&fromage=any&limit=10&sort=&psf=advsrch"
            yield scrapy.Request(url, \
                      meta={'state':st,'region':re,'geoid':geoid})

    def parse(self, response):
        base = response.request.url
        item = IndeedItem()
        count_ = response.xpath(".//div[@id='searchCount']/text()").extract()[0]
        tokens = count_.split(' ')
        count = tokens[-2]
        item['job_count'] = count
        item['state'] = response.meta['state']
        item['geoid'] = response.meta['geoid']
        item['region'] = response.meta['region']
        return item
