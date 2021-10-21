from requests_proxy import RequestsProxy
from parser_proxy import ParserProxy


class Scraper:
    def __init__(self):
        self.parser = ParserProxy()

    def get_artist_url(self, artist_name: str) -> str:
        url = 'https://www.lyrics.com/lyrics/%s' % artist_name
        html = RequestsProxy.get(url)
        return 'https://www.lyrics.com/' + self.parser.parse_artist_url(html, artist_name)

    def get_lyrics_url_by_song_dict(self, artist_url: str) -> dict:
        html = RequestsProxy.get(artist_url)

        return self.parser.get_lyrics_url_by_song_dict(html)

    def parse_lyrics(self, url):
        html = RequestsProxy.get('https://www.lyrics.com' + url)

        return self.parser.parse_lyrics(html)
