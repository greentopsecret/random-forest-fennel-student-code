import logging
import requests

from src.PostgreSQLClient import PostgreSQLClient


class TGNotifier:
    db_client: PostgreSQLClient

    def __init__(self, db_client, api_url, bot_token):
        self.api_url = api_url
        self.bot_token = bot_token
        self.db_client = db_client
        self.logger = logging.getLogger(self.__class__.__name__)

    def send_notification(self, ad):
        text = self._prepare_notification(ad)
        chats_id = self.db_client.find_chats_by_ad(ad)
        for chat_id in chats_id:
            url = 'https://%s/bot%s/sendMessage' % (self.api_url, self.bot_token)
            self.logger.debug('TG api endpoint {}'.format(url))
            body = {'chat_id': chat_id, 'parse_mode': 'markdown', 'text': text}
            self.logger.debug('TG api body {}'.format(body))
            response = requests.post(url=url, data=body)
            if response.status_code == 200:
                self.logger.info('Notification about ad#%d has been sent to user_id=%d' % (ad['index'], chat_id))
            else:
                self.logger.error('Notification about ad#%d has not been sent (user_id=%d, %s)' %
                                  (ad['index'], chat_id, response.content))

    def _prepare_notification(self, ad):
        self.logger.debug(ad.keys())
        self.logger.debug(ad.values())
        return '''
New ad from ebay 👻 
[{title}]({link})
Location: {location}
Price: {price}
Received at: {received_at}
[ ]({img})
        '''.format(**ad)
