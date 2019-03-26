# -*- coding: utf-8 -*-

# Scrapy settings for craigslist project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'craiglist'

SPIDER_MODULES = ['craiglist.spiders']
NEWSPIDER_MODULE = 'craiglist.spiders'
#TODO: changed below from list to dict to satisfy current scrapy
ITEM_PIPELINES = {} #{'craiglist.pipelines.TutorialPipeline' : 0}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'craigslist (+http://www.yourdomain.com)'

'''
DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': 'Project2015',
    'database': 'craiglist'
}
'''
