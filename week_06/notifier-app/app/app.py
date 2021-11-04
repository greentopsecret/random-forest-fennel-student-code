import requests
from dotenv import load_dotenv
import schedule
import time
import argparse
import os
import logging

from sqlalchemy import create_engine


class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(self.__class__.__name__)

    def send_notification(self, ad):
        response = requests.post(url=self.webhook_url, json=self._prepare_notification(ad))
        if response.status_code == 200:
            self.logger.info('Notification about ad#%d has been sent' % ad['index'])
        else:
            self.logger.error('Notification about ad#%d has not been sent (%s)' % (ad['index'], response.content))

    def _prepare_notification(self, ad):
        text = '''
        *New second hand bike on ebay 👻*
        {title}   
   
        {desc}   
        {price_raw}   
        {location}
        {link}   '''.format(**ad)

        return {
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': text
                    },
                    'accessory': {
                        'type': 'image',
                        'image_url': ad['img'],
                        'alt_text': ''
                    }
                }
            ]
        }


class App:

    def __init__(self):
        self.var_folder = './var/'
        args = self.__get_args()

        App.__load_dotenv(args.env)
        App.__init_logger(args.verbose)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.posgresql_client = PostgreSQLClient(
            os.getenv('POSTGRES_HOST'),
            os.getenv('POSTGRES_PORT'),
            os.getenv('POSTGRES_USER'),
            os.getenv('POSTGRES_PASSWORD'),
            os.getenv('POSTGRES_DBNAME')
        )
        self.notifier = SlackNotifier(os.getenv('SLACK_WEBHOOK_URL'))

    def run(self):

        self.logger.debug('Command is running')

        last_sent_ad_id = self.find_last_sent_ad()
        if last_sent_ad_id:
            self.logger.debug('Found last sent ad#%d' % last_sent_ad_id)
            new_ads = self.posgresql_client.find_ads_since(last_sent_ad_id)

            self.logger.debug('Found %d new ads' % len(new_ads))

            if new_ads:
                for ad in new_ads:
                    self.notifier.send_notification(ad)
                    self.store_last_sent_ad(ad['index'])
                    time.sleep(30)  # TODO: configure via args
        else:
            self.logger.debug('Last ad was not found')

            last_ad = self.posgresql_client.find_last_ad()

            self.logger.debug('Pulled last ad#%d from DB' % last_ad['index'])
            self.store_last_sent_ad(last_ad['index'])

    @staticmethod
    def __get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Send slack notifications in case of new second hand bikes in Berlin',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-v', '--verbose', default=0, action='count')
        parser.add_argument('-e', '--env',
                            help='Load specific environment config (f.e. use "--env local" to load .env.local config')

        return parser.parse_args()

    @staticmethod
    def __init_logger(verbosity: int):
        _format = '%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
        if verbosity == 1:
            level = logging.INFO
        elif verbosity > 2:
            level = logging.DEBUG
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

    def find_last_sent_ad(self):
        try:
            f = open(self.var_folder + '/last_sent_ad.txt', 'r')
        except Exception as e:
            return None

        i = f.readline()

        return int(i) if i else None

    def store_last_sent_ad(self, index: int):
        f = open(self.var_folder + '/last_sent_ad.txt', 'w')
        f.write(str(index))
        f.close()


class PostgreSQLClient:
    def __init__(self, host, port, user, password, database):
        port = int(port)
        uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri, echo=False)

    def find_last_ad(self) -> dict:
        sql = 'SELECT * FROM ads ORDER BY index DESC LIMIT 1'

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchone()

    def find_ads_since(self, index: int):
        sql = 'SELECT * FROM ads WHERE index > %d ORDER BY index ASC' % index

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()


if __name__ == '__main__':

    app = App()
    app.run()

    interval = 30
    schedule.every(interval).seconds.do(app.run)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logging.error(str(e))
            time.sleep(5)
