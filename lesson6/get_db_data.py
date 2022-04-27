import json
from bson.json_util import dumps

from pymongo import MongoClient

from jobparser.pipelines import MONGODB_URI, DB_NAME


def save_json(cursor, name):
    with open(name if 'json' in name else f'{name}.json', 'w') as f:
        json.dump(json.loads(dumps(cursor)), f, indent=2, ensure_ascii=False)


def save_hh(db):
    collection = db['hhru']
    vacancies_cur = collection.find({})
    save_json(vacancies_cur, 'hhData')


def save_superjob(db):
    collection = db['superjob']
    vacancies_cur = collection.find({})
    save_json(vacancies_cur, 'superjobData')


def main():
    mongodb = MongoClient(MONGODB_URI)
    db = mongodb[DB_NAME]
    save_hh(db)
    save_superjob(db)


if __name__ == '__main__':
    main()
