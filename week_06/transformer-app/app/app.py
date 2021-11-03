import argparse
import schedule
import time
import pymongo
import logging
import os
import re
import pandas as pd
from dotenv import load_dotenv
from bson.objectid import ObjectId
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import Table
from sqlalchemy import MetaData


class MongoDBClient:
    def __init__(self, dbname, host, port, username, password, collection):
        self.logger = logging.getLogger(self.__class__.__name__)
        port = int(port) if port else None
        self.logger.debug('Connect to PostgreSQL with parameters %s' % {'dbname': dbname, 'host': host, 'port': port,
                                                                        'username': username, 'password': password})
        client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.collection = client[dbname].get_collection(collection)

    def find_younger_than(self, last_ad) -> list:
        filter_ = {'_id': {'$gt': ObjectId(last_ad['incoming_id'])}} if last_ad else {}
        return list(self.collection.find(filter_))


class PostgreSQLClient:
    def __init__(self, host, port, user, password, database):
        port = int(port) if port else None
        uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri, echo=False)
        pass

    def find_last_ad(self) -> dict:
        sql = 'SELECT incoming_id FROM ads ORDER BY index DESC LIMIT 1'

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchone()

    def store(self, ads):
        table = Table('ads', MetaData(self.engine), autoload_with=self.engine)

        for ad in ads:
            with self.engine.connect() as conn:
                stmt = insert(table).values(ad)
                conn.execute(stmt)


class EbayAdsTransformer:
    PROVIDER_NAME = 'ebay'

    def __init__(self):
        pass

    def transform(self, ads):

        for ad in ads:
            ad['price_raw'] = ad['price']
            if re.search(r'Zu verschenken', ad['price']):
                ad['price_comment'] = 'give away'
            elif re.search(r' VB', ad['price']):
                ad['price_comment'] = 'negotiation'
            else:
                ad['price_comment'] = ''
            price = re.sub(r'[^\d]', '', ad['price'])
            ad['price'] = int(price) if price else 0
            ad['provider'] = EbayAdsTransformer.PROVIDER_NAME
            ad['incoming_id'] = str(ad['_id'])
            del ad['_id']

        return ads


class App:
    def __init__(self):
        args = App.__get_args()

        App.__load_dotenv(args.env)

        self.data_transformer = EbayAdsTransformer()
        self.mongodb_client = MongoDBClient(
            os.getenv('MONGODB_NAME'),
            os.getenv('MONGODB_HOST'),
            os.getenv('MONGODB_PORT'),
            os.getenv('MONGODB_USERNAME'),
            os.getenv('MONGODB_PASSWORD'),
            'ebay_ads'
        )
        self.posgresql_client = PostgreSQLClient(
            os.getenv('POSTGRESQL_HOST'),
            os.getenv('POSTGRESQL_PORT'),
            os.getenv('POSTGRESQL_USER'),
            os.getenv('POSTGRESQL_PASSWORD'),
            os.getenv('POSTGRESQL_DBNAME')
        )

    def run(self):
        last_ad = self.posgresql_client.find_last_ad() # TODO: add a property with the last_ad
        new_ads = self.mongodb_client.find_younger_than(last_ad)
        new_ads = self.data_transformer.transform(new_ads)
        self.posgresql_client.store(new_ads)

    @staticmethod
    def __get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Transform raw data (from MongoDB) to relational DB (PostgreSQL)',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-e', '--env',
                            help='Load specific environment config (f.e. use "--env local" to load .env.local config')
        parser.add_argument('-v', '--verbose', default=0, action='count')

        return parser.parse_args()

    @staticmethod
    def __load_dotenv(env):
        """
        Method loads config file based on passed value.
        :param env: config file postfix. For example file .env.local will be loaded for env=local
        :return: void
        """
        if env:
            filename = '%s/.env.%s' % (os.path.dirname(os.path.realpath(__file__)), env)
            load_dotenv(dotenv_path=filename)


if __name__ == '__main__':
    schedule.every(2).to(5).seconds.do(App().run)
    while True:
        schedule.run_pending()
        time.sleep(5)
