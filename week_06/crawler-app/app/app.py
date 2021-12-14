import argparse
import os
import logging
import random

from attrdict import AttrDict
import mechanicalsoup
import pymongo
from dotenv import load_dotenv
from datetime import datetime
import schedule
import time
from http.client import HTTPConnection


class EbayCrawler:
    URL_TEMPLATE = '%s/s-wohnung-mieten/berlin/anzeige:angebote/seite:%d/c203l3331+wohnung_mieten.qm_d:35,'

    def __init__(self, host, cnt):
        self.cnt = cnt
        self.host = host.strip('/')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser = mechanicalsoup.Browser(
            soup_config={'features': 'lxml'},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        )

    def pull_data(self) -> list:

        self.logger.debug('Start pulling data')

        result = []
        for page in range(1, self.cnt + 1):
            for ad in self.__get_page_ads(page):
                result.append(ad)
            time.sleep(random.randint(3, 10))

        self.logger.debug('Found %d ads' % len(result))

        return result

    def __get_page_ads(self, page: int) -> list:
        url = self.build_page_url(page)

        self.logger.debug('Pull data from %s' % url)

        results = []
        try:
            response = self.browser.get(url)
            self.logger.debug('response.status_code: %s', response.status_code)
        except Exception as e:
            self.logger.error('Request to ebay failed. %s' % str(e))
            raise e

        if response.status_code != 200:
            raise Exception('Request to ebay returned status code %d' % response.status_code)

        for el in response.soup.select('article.aditem'):
            out = AttrDict()

            img = el.select('[data-imgsrc]')
            out.img = img[0].attrs['data-imgsrc'] if len(img) else None

            out.provider_id = el.attrs['data-adid']
            out.link = self.host + el.select('a[href^="/s-anzeige"]')[0].attrs['href']
            out.title = el.select('.text-module-begin a')[0].text.strip()
            out.desc = el.select('.aditem-main p')[0].text.strip()
            out.price = el.select('.aditem-main--middle--price')[0].text.strip()
            out.location = el.select('.aditem-main--top--left')[0].text.strip()
            out.received_at = datetime.now()

            results.append(out)

        return results

    def build_page_url(self, page: int):
        return EbayCrawler.URL_TEMPLATE % (self.host, page)


class DBClient:
    def __init__(self, dbname, host, port, username, password, collection_name):
        self.logger = logging.getLogger(self.__class__.__name__)
        port = int(port) if port else None
        self.logger.debug('Connect to MongoDB with parameters %s' % {'dbname': dbname, 'host': host, 'port': port,
                                                                     'username': username, 'password': password})
        client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.collection = client[dbname].get_collection(collection_name)

    def insert(self, ads: list) -> int:
        cnt = 0
        for ad in ads:
            # TODO: Check update_many
            result = self.collection.update_one(
                {'provider_id': ad.provider_id},
                {'$set': ad},
                upsert=True
            )
            if not result.raw_result['updatedExisting']:
                cnt += 1
                # self.logger.debug(result.modified_count)
                # self.logger.debug(result.acknowledged)
                # self.logger.debug(result.upserted_id)

        self.logger.debug('Number of inserted documents %d' % cnt)


class App:

    def __init__(self):
        args = App.__get_args()

        App.__load_dotenv(args.env)
        App.__init_logger(args.verbose)

        self.crawler = EbayCrawler(os.getenv('EBAY_HOST'), args.cnt)

        self.db_client = DBClient(
            os.getenv('MONGODB_NAME'),
            os.getenv('MONGODB_HOST'),
            os.getenv('MONGODB_PORT'),
            os.getenv('DB_USERNAME'),
            os.getenv('DB_PASSWORD'),
            'ebay_ads'
        )

    def run(self):
        data = self.crawler.pull_data()
        self.db_client.insert(data)

    @staticmethod
    def __get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Crawl ebay kleinanzeigen',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-c', '--cnt', default=3, type=int, help='Number of result pages to crawl')
        parser.add_argument('-v', '--verbose', default=0, action='count')
        parser.add_argument('-e', '--env',
                            help='Load specific environment config (f.e. use "--env local" to load .env.local config')

        return parser.parse_args()

    @staticmethod
    def __init_logger(verbosity: int):
        _format = '%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
        if verbosity == 1:
            level = logging.INFO
        elif verbosity == 2:
            level = logging.DEBUG
        elif verbosity > 2:
            level = logging.DEBUG
            HTTPConnection.debuglevel = 1
        else:
            level = logging.WARNING

        logging.basicConfig(level=level, format=_format)

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

    app = App()
    app.run()

    min_interval = 2  # TODO: set up via arguments
    max_interval = 4
    schedule.every(min_interval * 60).to(max_interval * 60).seconds.do(app.run)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.error(str(e))
            time.sleep(5)
