import json
from bson.json_util import dumps

from pymongo import MongoClient

from hardwarestore.spiders.leroymerlin import LeroymerlinSpider
from hardwarestore.pipelines import MONGODB_URI


def save_json(cursor, name):
    with open(name if 'json' in name else f'{name}.json', 'w') as f:
        json.dump(json.loads(dumps(cursor)), f, indent=2, ensure_ascii=False)


def save_leroymerlin(client):
    db = client[LeroymerlinSpider.name]
    collection = db['lyustry']
    chandeliers_cur = collection.find({})
    save_json(chandeliers_cur, 'leroyChandeliers')


def main():
    mongodb = MongoClient(MONGODB_URI)
    save_leroymerlin(mongodb)


if __name__ == '__main__':
    main()
