# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class JingdongItem(Item):
    pid = Field()
    name = Field()
    url = Field()
    price = Field()
    image = Field()
    comments = Field()
    rate = Field()
    cat_key = Field()
    cat_value = Field()
    args = Field()
    category = Field()
    ref = Field()
