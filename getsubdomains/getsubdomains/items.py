# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class GetsubdomainsItem(Item):
    # define the fields for your item here like:
    subdomain = Field()
    region = Field()
    state = Field()
    def __repr__(self):
        # don't print anything:
        # https://stackoverflow.com/questions/14390945/suppress-scrapy-item-printed-in-logs-after-pipeline/16303725
        return repr({})
