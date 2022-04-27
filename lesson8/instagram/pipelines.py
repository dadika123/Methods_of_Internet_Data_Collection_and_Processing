# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

from instagram.items import InstagramUserItem

MONGODB_URI = '127.0.0.1:27017'


class InstagramPipeline:
    def __init__(self):
        self.mongodb = MongoClient(MONGODB_URI)

    def process_item(self, item, spider):
        self.update_db(item, spider)
        return item

    def update_db(self, item, spider):
        db = self.mongodb[f'ig_{item["caller_username"]}']
        collection = db[item['type']]
        del item['type']
        del item['caller_username']
        if 'search_index' not in collection.index_information():
            collection.create_index('pk', name='search_index', unique=True)
        collection.replace_one({'pk': item['pk']}, item, upsert=True)


class InstagramImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f'{info.spider.name}/{item["username"]}.jpg'
