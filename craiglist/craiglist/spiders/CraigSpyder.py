# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html
from items import CraigslistItem
import pandas as pd


class MySpider(CrawlSpider): 
    name = "craig"
    allowed_domains = ["craigslist.org"]
    sub_domains = list(pd.read_csv("subs.csv")["subdomain"])
    start_urls = ("https://" + sd + ".craigslist.org/search/see/apa?" for sd in sub_domains) # iterator

    # https://stackoverflow.com/questions/32624033/scrapy-crawl-with-next-page
    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="button next"]',)), callback="parse_page", follow= True),)

    def parse_page(self, response):
        base = response.request.url

        #find all postings
        postings = response.xpath(".//p[@class='result-info']") # pure selectors
        #loop through the postings
        for i in range(0, len(postings)-1):
            item = CraigslistItem()
            ex1 = postings[i].xpath("a/@data-id")
            ex2 = postings[i].xpath("time/text()")
            ex3 = postings[i].xpath("a/text()")
            ex4 = postings[i].xpath("span[@class='result-meta']/span[@class='result-price']/text()")
            ex5 = postings[i].xpath("a/@href")
            #post id
            item["craigId"] = int(''.join(ex1.extract()))
            #date of posting
            item["date"] = ''.join(ex2.extract())
            #title of posting
            item["title"] = ''.join(ex3.extract())
            #pre-processing for getting the price in the right format
            price = ''.join(ex4.extract())
            item["price"] = price.replace("$","")
            item["link"] = ''.join(ex5.extract())
            follow = item["link"] 
            #Parse request to follow the posting link into the actual post
            request = scrapy.Request(follow , callback=self.parse_item_page)
            request.meta['item'] = item
            yield request

    #Parsing method to grab items from inside the individual postings
    #To modify, inspect the XML of the webpages to find out where each piece of data is
    def parse_item_page(self, response):
        # geolocation
        item = response.meta["item"]
        maplocation = response.xpath("//div[contains(@id,'map')]") #also in mapAndAttrs
        latitude = ''.join(maplocation.xpath('@data-latitude').extract())
        longitude = ''.join(maplocation.xpath('@data-longitude').extract())
        if latitude:
            item['latitude'] = float(latitude)
        if longitude:
            item['longitude'] = float(longitude)

        # bed, bath, size
        attr = response.xpath("//p[@class='attrgroup']/span[@class='shared-line-bubble']")
        for a in attr:
            if (a.xpath("text()").extract() == "ft" or a.xpath("text()")[0].extract() == "ft"):
                size = a.xpath("b/text()")
                if isinstance(size, (str,)):
                    item["size"] = int(size.extract()) 
                if isinstance(size, (list,)):
                    item["size"] = int(size[0].extract())
            else:
                bnb = a.xpath("b/text()")
                for b in bnb:
                    suffix = b.extract()[-2:]
                    if (suffix == "BR"):
                        item["beds"] = int(bnb[0].extract()[:-2]) 
                    elif (suffix == "Ba"):
                        item["baths"] = float(bnb[1].extract()[:-2])

        item["contentLen"] = len(response.xpath("//section[@id='postingbody']").xpath("text()").extract())
        postinginfo = response.xpath("//p[@class = 'postinginfo reveal']").xpath("time/@datetime")
        item["postDate"] = postinginfo.extract()
        item["updateDate"] = postinginfo.extract()
        if item["updateDate"] != item["postDate"]:
            item["reposts"] = 1
        else:
            item["reposts"] = 0
        item["numPic"] = len(response.xpath("//div[@id='thumbs']").xpath("a"))
        return item
