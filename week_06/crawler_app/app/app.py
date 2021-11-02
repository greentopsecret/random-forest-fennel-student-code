#!/usr/bin/env python3

import argparse
import os
import logging
from dotenv import load_dotenv
from attrdict import AttrDict
import mechanicalsoup
import pymongo
from datetime import datetime
import schedule
import time
from http.client import HTTPConnection


class EbayCrawler:
    URL_TEMPLATE = 'https://www.ebay-kleinanzeigen.de/s-fahrraeder/anzeige:angebote/seite:%d/fahrrad/k0c217'

    def __init__(self, cnt):
        self.cnt = cnt
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser = mechanicalsoup.Browser(
            soup_config={'features': 'lxml'},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        )

    def pull_data(self) -> list:

        self.logger.debug('Start pulling data')

        result = []
        for page in range(1, self.cnt + 1):

            for ad in self.__get_page_ads(page):
                result.append(ad)

        self.logger.debug('Found %d ads' % len(result))

        return result

    def __get_page_ads(self, page: int) -> list:
        url = EbayCrawler.build_page_url(page)
        page = self.browser.get(url)
        domain = '/'.join(url.split('/')[0:3])
        results = []
        for el in page.soup.select('article.aditem'):
            out = AttrDict()

            img = el.select('[data-imgsrc]')
            out.img = img[0].attrs['data-imgsrc'] if len(img) else None

            out.internal_id = el.attrs['data-adid']
            out.link = domain + el.select('a[href^="/s-anzeige"]')[0].attrs['href']
            out.title = el.select('.text-module-begin a')[0].text.strip()
            out.desc = el.select('.aditem-main p')[0].text.strip()
            out.price = el.select('.aditem-main--middle--price')[0].text.strip()
            out.location = el.select('.aditem-main--top--left')[0].text.strip()
            out.received_at = datetime.now()

            results.append(out)

        return results

    @staticmethod
    def build_page_url(page: int):
        return EbayCrawler.URL_TEMPLATE % page


class DBClient:
    def __init__(self, dbname, host, port, username, password, collection):
        self.logger = logging.getLogger(self.__class__.__name__)
        port = int(port) if port else None
        self.logger.debug('Connect to MongoDB with parameters %s' % {'dbname': dbname, 'host': host, 'port': port,
                                                                     'username': username, 'password': password})
        client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.db = client[dbname]
        self.collection = collection

    def insert(self, ads: list):
        for ad in ads:
            result = self.db.get_collection(self.collection).update_one(
                {'internal_id': ad.internal_id},
                {'$set': ad},
                upsert=True
            )
        # self.db['ads'].insert_many(ads)


class App:

    def __init__(self):
        args = self.__get_args()

        App.__init_logger(args.verbose)

        self.crawler = EbayCrawler(args.cnt)

        load_dotenv()
        self.db_client = DBClient(
            os.getenv('DB_NAME'),
            os.getenv('DB_HOST'),
            os.getenv('DB_PORT'),
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


if __name__ == '__main__':
    min_interval = 3  # TODO: set up via arguments
    max_interval = 5
    schedule.every(min_interval * 60).to(max_interval * 60).seconds.do(App().run)
    while True:
        schedule.run_pending()
        time.sleep(1)
