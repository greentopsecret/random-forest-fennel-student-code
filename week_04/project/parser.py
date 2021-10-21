from bs4 import BeautifulSoup
import re


class Parser:
    __verbose = False

    @staticmethod
    def verbose():
        Parser.__verbose = True

    def get_lyrics_url_by_song_dict(self, html: str) -> dict:
        result = {}
        table_list = BeautifulSoup(html, 'html.parser').find_all('table', class_='tdata')
        if not table_list:
            raise Exception('Cannot parse list of songs (no table)')

        for table in table_list:

            tbody_list = table.find_all('tbody')
            if not tbody_list:
                raise Exception('Cannot parse list of songs (no tbody)')

            for tbody in tbody_list:

                tr_list = tbody.find_all('tr')
                if not tr_list:
                    raise Exception('Cannot parse list of songs (no tr)')

                for tr in tr_list:
                    link = tr.find_all('td')[0].find('a')
                    song_name = link.text.lower()
                    song_name = re.sub(r'[,\.:\'"]', '', song_name)
                    song_name = re.sub(r'[\[\()][\w -]+[\]\)]', '',
                                       song_name)  # remove strings like "[live]" or "[immortal version]"
                    song_name = song_name.strip()
                    result[song_name] = link.attrs['href']

        return result

    def parse_lyrics(self, html: str) -> str:
        text = BeautifulSoup(html, 'html.parser').find(id='lyric-body-text')
        if not text:
            raise Exception('No song found')
        return text.text

    @staticmethod
    def parse_artist_url(html: str, artist_name: str) -> str:
        a = BeautifulSoup(html, 'html.parser').find('a', title=artist_name, class_='name')
        if not a:
            raise Exception('Cannot find artist "%s"' % artist_name)

        return a.attrs['href']
