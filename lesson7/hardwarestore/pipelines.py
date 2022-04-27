# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

MONGODB_URI = '127.0.0.1:27017'


class HardwarestorePipeline:
    def __init__(self):
        self.mongodb = MongoClient(MONGODB_URI)

    def process_item(self, item, spider):
        self.update_db(item, spider)
        return item

    def update_db(self, item, spider):
        db = self.mongodb[spider.name]
        collection = db[spider.cat]
        if 'search_index' not in collection.index_information():
            collection.create_index('url', name='search_index', unique=True)
        collection.replace_one({'url': item['url']}, item, upsert=True)


class HardwarestoreImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        dir_name = re.sub(r'[^\w\-_\. ]', '_', item['name'])
        return f'{info.spider.name}/{info.spider.cat}/{dir_name}/{item["photos"].index(request.url)}.jpg'
