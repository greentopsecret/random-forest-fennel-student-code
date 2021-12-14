class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(self.__class__.__name__)

    def send_notification(self, ad):
        # self.logger.debug('Send notification {}'.format(ad))
        response = requests.post(url=self.webhook_url, json=self._prepare_notification(ad))
        if response.status_code == 200:
            self.logger.info('Notification about ad#%d has been sent' % ad['index'])
        else:
            self.logger.error('Notification about ad#%d has not been sent (%s)' % (ad['index'], response.content))

    def _prepare_notification(self, ad):
        text = '''
New second hand bike on ebay 👻
*{title}*   

{price_raw}   
{location}
{link}   
        '''.format(**ad)

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
                        'alt_text': ad['desc']
                    }
                }
            ]
        }