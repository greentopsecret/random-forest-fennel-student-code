#!/usr/bin/env python3

import argparse
import os
import logging
from dotenv import load_dotenv
from attrdict import AttrDict
import mechanicalsoup
import pymongo
from datetime import datetime


class EbayCrawler:
    URL_TEMPLATE = 'https://www.ebay-kleinanzeigen.de/s-fahrraeder/anzeige:angebote/seite:%d/fahrrad/k0c217'

    def __init__(self, cnt=5):
        self.cnt = cnt
        self.browser = mechanicalsoup.Browser(
            soup_config={'features': 'lxml'},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        )

    def crawl_data(self) -> list:
        result = []
        for page in range(1, self.cnt):

            for ad in self.__get_page_ads(page):
                result.append(ad)

        return result

    def __get_page_ads(self, page: int) -> list:
        url = EbayCrawler.build_page_url(page)
        page = self.browser.get(url)
        # Dirty
        domain = '/'.join(url.split('/')[0:3])
        results = []
        for el in page.soup.select('article.aditem'):
            out = AttrDict()

            img = el.select('[data-imgsrc]')
            out.img = img[0].attrs['data-imgsrc'] if len(img) else None

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
    def __init__(self, dbname, host, port, username, password):
        # self.dbname = dbname
        # self.host = host
        # self.username = username
        # self.password = password

        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[dbname]

    def insert(self, ads: list):
        self.db['ads'].insert_many(ads)


class App:

    def __init__(self):
        args = self.__get_args()
        self.crawler = EbayCrawler(args.cnt)

        load_dotenv()
        self.db_client = DBClient(
            os.getenv('DB_NAME'),
            os.getenv('DB_HOST'),
            os.getenv('DB_PORT'),
            os.getenv('DB_USERNAME'),
            os.getenv('DB_PASSWORD')
        )

        # TODO: set verbosity level based on args.verbosity

    def run(self):
        data = self.crawler.crawl_data()
        self.db_client.insert(data)

    @staticmethod
    def __get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Crawl ebay kleinanzeigen',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-c', '--cnt', default=3, type=int, help='Number of result pages to crawl')
        parser.add_argument('--verbose', default=False, action=argparse.BooleanOptionalAction)

        return parser.parse_args()


if __name__ == '__main__':
    App().run()
