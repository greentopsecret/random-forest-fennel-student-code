import requests
from bs4 import BeautifulSoup

class ScraperRemote:

    def get_songs_list_html(self, url):
        # print('url: %s' % url)
        return requests.get(url).text

    def get_lyrics_html(self, url):
        # print('url: %s' % url)
        return requests.get(url).text