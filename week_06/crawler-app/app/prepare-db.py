#!/usr/bin/env python3

from dotenv import load_dotenv
import os
import pymongo


class DbLoader:
    def __init__(self, dbname, host, port, username, password, collection):
        port = int(port) if port else None
        username = username if username else None
        password = password if password else None
        client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.db = client[dbname]
        self.collection_name = collection

    def run(self):
        self.add_unique_index()

    def add_unique_index(self):
        self.db[self.collection_name].create_index([('provider_id', pymongo.ASCENDING)], unique=True)


if __name__ == '__main__':
    load_dotenv()
    DbLoader(
        os.getenv('MONGODB_NAME'),
        os.getenv('MONGODB_HOST'),
        os.getenv('MONGODB_PORT'),
        os.getenv('DB_USERNAME'),
        os.getenv('DB_PASSWORD'),
        'ebay_ads'
    ).run()
    print('done')
