# -*- coding: utf-8 -*-

import scrapy


class CountItem(scrapy.Item):
    geoid = scrapy.Field()
    state = scrapy.Field()
    region = scrapy.Field()
    place = scrapy.Field()
    count = scrapy.Field() 
    minwage = scrapy.Field()
