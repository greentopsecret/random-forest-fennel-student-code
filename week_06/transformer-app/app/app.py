import argparse
from datetime import datetime
import schedule
import time
import pymongo
import logging
import os
import re
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

    def find_newer_than(self, last_ad) -> list:
        filter_ = {'_id': {'$gt': ObjectId(last_ad['incoming_id'])}} if last_ad else {}
        return list(self.collection.find(filter_))


class PostgreSQLClient:
    def __init__(self, host, port, user, password, database):
        port = int(port)
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
            ad['transformed_at'] = datetime.now()

            # TODO: add transformed_at

            del ad['_id']

        return ads


class App:
    def __init__(self):
        args = App.__get_args()

        App.__load_dotenv(args.env)
        App.__init_logger(args.verbose)

        self.logger = logging.getLogger(self.__class__.__name__)

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
            os.getenv('POSTGRES_HOST'),
            os.getenv('POSTGRES_PORT'),
            os.getenv('POSTGRES_USER'),
            os.getenv('POSTGRES_PASSWORD'),
            os.getenv('POSTGRES_DBNAME')
        )

    def run(self):
        self.logger.info('Start')

        last_ad = self.posgresql_client.find_last_ad()  # TODO: add a property with the last_ad

        self.logger.debug('Found last_ad: %s' % str(last_ad))

        new_ads = self.mongodb_client.find_newer_than(last_ad)

        self.logger.debug('Found %d new ads' % len(new_ads))

        new_ads = self.data_transformer.transform(new_ads)
        self.posgresql_client.store(new_ads)

        self.logger.info('End. Transformed and loaded %d new ads.' % len(new_ads))

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

    @staticmethod
    def __init_logger(verbosity: int):
        _format = '%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
        if verbosity == 1:
            level = logging.INFO
        elif verbosity > 1:
            level = logging.DEBUG
        else:
            level = logging.WARNING

        logging.basicConfig(level=level, format=_format)


if __name__ == '__main__':
    # App().run()
    # sys.exit(1)

    app = App()
    app.run()

    interval = 3  # TODO: set up via arguments
    schedule.every(interval * 60).seconds.do(app.run)

    while True:
        schedule.run_pending()
        time.sleep(5)