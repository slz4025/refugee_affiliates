# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

'''
class CraiglistItem(Item):
    title = Field()
    link = Field()
'''

#Item class with listed fields to scrape
class CraigslistItem(Item):
    date = Field()
    title = Field()
    link = Field()
    price = Field()
    #area = Field()
    beds = Field()
    size = Field()
    craigId = Field()
    numPic = Field()
    postDate = Field()
    updateDate = Field()
    baths = Field()
    latitude = Field()
    longitude = Field()
    contentLen = Field()
    reposts = Field()
    zipcode = Field()
    state = Field()
    region = Field()
    subdomain = Field()
    def __repr__(self):
        # don't print anything:
        # https://stackoverflow.com/questions/14390945/suppress-scrapy-item-printed-in-logs-after-pipeline/16303725
        return repr({})
