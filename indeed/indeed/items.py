# -*- coding: utf-8 -*-

import scrapy


class IndeedItem(scrapy.Item):
    geoid = scrapy.Field()
    region = scrapy.Field()
    state = scrapy.Field()
    job_count = scrapy.Field()
    def __repr__(self):
        # don't print anything:
        # https://stackoverflow.com/questions/14390945/suppress-scrapy-item-printed-in-logs-after-pipeline/16303725
        return repr({})
