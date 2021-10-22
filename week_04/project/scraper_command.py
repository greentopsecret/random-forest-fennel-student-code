import numpy as np

from model import Model
from tqdm import tqdm
import pandas as pd
import sys
import os
import argparse
from requests_proxy import RequestsProxy
from parser_proxy import ParserProxy
from scraper import Scraper
import re


class ScraperCommand:

    def __init__(self):
        self.model = Model()
        self.scraper = Scraper()

    def exec(self):
        args = ScraperCommand.__get_args()
        if args.verbose:
            RequestsProxy.verbose()
            ParserProxy.verbose()

        if args.cache_folder:
            RequestsProxy.set_cache_folder(args.cache_folder)

        try:
            artist_name1 = args.artist1 if args.artist1 else input('Enter the first artist name: ')
            lyrics_list1, artists_list1 = self.get_artist_data(artist_name1, args.cnt)
            artist_name2 = args.artist2 if args.artist2 else input('Enter the second artist name: ')
            lyrics_list2, artists_list2 = self.get_artist_data(artist_name2, args.cnt)
        except Exception as e:
            print(e)
            sys.exit()

        lyrics_list = pd.Series(lyrics_list1 + lyrics_list2, name='lyrics')
        artists_list = pd.Series(artists_list1 + artists_list2, name='artist')

        output_file_name = self.build_output_filename(artists_list.unique(), args.cnt)
        self.store_data(lyrics_list, artists_list, output_file_name)

        print('Lyrics data stored into %s' % output_file_name)

    def get_artist_data(self, artist_name, limit) -> (list, list):

        artist_url = self.scraper.get_artist_url(artist_name)

        # Search artist and get its list of songs
        lyrics_url_by_song = self.scraper.get_lyrics_url_by_song_dict(artist_url)

        lyrics_list = []
        artists_list = []

        # Go through artist's songs and pull lyrics
        for song_name, url in tqdm(lyrics_url_by_song.items()):
            try:
                lyrics = self.scraper.parse_lyrics(url)
            except Exception as e:  # catch *all* exceptions
                print('Cannot get "%s" from %s (%s)' % (song_name, url, str(e)))
                continue

            lyrics_list.append(Model.clean_lyrics(lyrics))
            artists_list.append(artist_name)

            if limit is not None and len(lyrics_list) >= limit:
                break

        return lyrics_list, artists_list

    @staticmethod
    def __get_args():
        parser = argparse.ArgumentParser(
            description="Command that scraps lyrics from lyrics.com and stores transformed data into the file",
            epilog='Example of usage: python scraper_command.py'
        )

        parser.add_argument('--cnt', help='load only N songs per artist', type=int)
        parser.add_argument('--artist1', help='Artist one name')
        parser.add_argument('--artist2', help='Artist one name')
        parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
        parser.add_argument('-c', '--cache-folder', help='path to the cache folder')

        return parser.parse_args()

    def store_data(self, lyrics_list: pd.Series, artists_list: pd.Series, output_file_name) -> str:

        f = open(output_file_name, 'w')
        f.write(pd.concat([lyrics_list, artists_list], axis=1).to_csv(sep=','))
        f.close()

        return output_file_name

    def build_output_filename(self, artists_list: np.ndarray, cnt: int) -> str:
        f = lambda x: re.sub(r'[^\w]', '', x.lower())
        v = np.vectorize(f)
        d = v(artists_list)

        return "%s/data/%s-%d.csv" % (
            os.path.dirname(os.path.realpath(__file__)),
            "-".join(d),
            cnt
        )


if __name__ == '__main__':
    ScraperCommand().exec()
