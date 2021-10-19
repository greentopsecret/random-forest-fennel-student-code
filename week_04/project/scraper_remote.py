import requests
from bs4 import BeautifulSoup

class ScraperRemote:

    def get_songs_list_html(self, url):
        # todo: cache this request

        return requests.get(url).text

    def get_lyrics(self, url):
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        return soup.find(id='lyric-body-text').text