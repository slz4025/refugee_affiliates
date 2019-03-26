# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html
from items import GetsubdomainsItem

class MySpider(scrapy.Spider):
    name = "craig"
    allowed_domains = ["craigslist.org"]
    start_urls = ["https://www.craigslist.org/about/sites"]

    def parse(self, response):
        US = response.xpath(".//div[@class='colmask']")[0]
        columns = US.xpath(".//div")
        states = [name.extract() for col in columns for name in col.xpath(".//h4/text()")]
        states_regions = [reg.xpath(".//li") for col in columns for reg in col.xpath(".//ul")]
        states_info = zip(states, states_regions)
        for state_name, state_regs in states_info:
            for reg in state_regs:
                item = GetsubdomainsItem()
                item["state"] = state_name 
                item["region"] = reg.xpath("a/text()").extract()
                sd = reg.xpath("a/@href").extract()[0] # get rid of "https://"
                sd = sd[8:sd.find('.')]
                item["subdomain"] = sd
                yield item
