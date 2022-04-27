# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

# from itemadapter import ItemAdapter
from pymongo import MongoClient

MONGODB_URI = '127.0.0.1:27017'
DB_NAME = 'scrapy_jobparser_db'
COLLECTION_NAME = 'vacancy'

SALARY_RE = re.compile(r'(\d+\s?\d+)')
CURRENCY_RE = re.compile(r'\d+\s+([a-zA-Zа-яА-я]+)\.*\s*[^\d]*$')


class JobparserPipeline:
    def __init__(self):
        self.mongodb = MongoClient(MONGODB_URI)
        self.db = self.mongodb[DB_NAME]

    def process_item(self, item, spider):
        salary = self.process_salary(item.get('salary'))
        item['salary_min'], item['salary_max'], item['currency'] = salary
        del item['salary']
        self.update_db(item, spider.name)

        return item

    def process_salary(self, raw_salary):
        if isinstance(raw_salary, list):
            raw_salary = ''.join(raw_salary)
        salary = raw_salary.replace(u'\xa0', ' ').replace(u'\u202f', ' ')
        salary_search = re.findall(SALARY_RE, salary)
        salary_min, salary_max, currency = '', '', ''

        if len(salary_search) == 1:
            currency = re.search(CURRENCY_RE, salary).group(1)
            salary_value = int(salary_search[0].replace(' ', ''))
            if 'от' in salary:
                salary_min = salary_value
            elif 'до' in salary:
                salary_max = salary_value
            else:
                salary_min = salary_value
        elif len(salary_search) == 2:
            currency = re.search(CURRENCY_RE, salary).group(1)
            salary_min, salary_max = int(salary_search[0].replace(' ', '')), int(salary_search[1].replace(' ', ''))

        return salary_min, salary_max, currency

    def update_db(self, item, collection_name):
        collection = self.db[collection_name]
        if 'search_index' not in collection.index_information():
            collection.create_index('url', name='search_index', unique=True)
        collection.replace_one({'url': item['url']}, item, upsert=True)
