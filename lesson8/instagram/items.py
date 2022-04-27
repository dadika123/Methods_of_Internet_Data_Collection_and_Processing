# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst


class InstagramItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class InstagramUserItem(scrapy.Item):
    caller_username = scrapy.Field(output_processor=TakeFirst())
    pk = scrapy.Field(output_processor=TakeFirst())
    username = scrapy.Field(output_processor=TakeFirst())
    full_name = scrapy.Field(output_processor=TakeFirst())
    photo = scrapy.Field(output_processor=TakeFirst())
    is_private = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
