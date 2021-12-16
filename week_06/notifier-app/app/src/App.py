import argparse
import logging
import os
import time
from dotenv import load_dotenv
from src.PostgreSQLClient import PostgreSQLClient
from src.TGNotifier import TGNotifier


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
        self.notifier = TGNotifier(self.posgresql_client, os.getenv('TG_API_URL'), os.getenv('TG_BOT_TOKEN'))

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
                    time.sleep(30)  # TODO: configure via args
                    # self.logger.debug('store last ad {}'.format(ad))
                    self.store_last_sent_ad(ad['index'])
        else:
            self.logger.debug('Last ad was not found')

            last_ad = self.posgresql_client.find_last_ad()

            self.logger.debug('Pulled last ad#%d from DB' % last_ad['index'])
            self.store_last_sent_ad(last_ad['index'])

    @staticmethod
    def __get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Bot that sends notifications in case of new apartment ad',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-v', '--verbose', default=0, action='count')
        parser.add_argument('-e', '--env',
                            help='Load specific environment config (f.e. use "--env local" to load .env config')

        return parser.parse_args()

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

    @staticmethod
    def __load_dotenv(env):
        """
        Method loads config file based on passed value.
        :param env: config file postfix. For example file .env will be loaded for env=local
        :return: void
        """
        # filename = '%s/../.env' % os.path.dirname(os.path.realpath(__file__))
        # if os.path.isfile(filename):
        #     load_dotenv(dotenv_path=filename)
        if env:
            filename = '%s/../.env.%s' % (os.path.dirname(os.path.realpath(__file__)), env)
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
