# Scrapy settings for lens project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'lens'

SPIDER_MODULES = ['lens.spiders']
NEWSPIDER_MODULE = 'lens.spiders'
ITEM_PIPELINES = ['lens.pipelines.LensPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'lens (+http://www.yourdomain.com)'
