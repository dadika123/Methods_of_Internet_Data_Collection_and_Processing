import json
from bson.json_util import dumps

from pymongo import MongoClient

from instagram.spiders.profiles import ProfilesSpider
from instagram.pipelines import MONGODB_URI


def save_json(cursor, name):
    with open(name if 'json' in name else f'{name}.json', 'w') as f:
        json.dump(json.loads(dumps(cursor)), f, indent=2, ensure_ascii=False)


def save_followers(client, username):
    db = client[f'ig_{username}']
    collection = db['followers']
    chandeliers_cur = collection.find({})
    save_json(chandeliers_cur, f'{username}Followers')


def save_following(client, username):
    db = client[f'ig_{username}']
    collection = db['following']
    chandeliers_cur = collection.find({})
    save_json(chandeliers_cur, f'{username}Following')


def main():
    mongodb = MongoClient(MONGODB_URI)
    save_followers(mongodb, 'kaenmuenchen')
    save_following(mongodb, 'kaenmuenchen')
    save_followers(mongodb, 'odessa_feinkost')
    save_following(mongodb, 'odessa_feinkost')


if __name__ == '__main__':
    main()
