from model import Model
from tqdm import tqdm
import numpy as np
import pandas as pd
import sys
import argparse
from requests_proxy import RequestsProxy
from parser_proxy import ParserProxy
from scraper import Scraper


class Command:

    def __init__(self):
        self.model = Model()
        self.scraper = Scraper()

    def exec(self):
        args = Command.__get_args()
        if args.verbose:
            RequestsProxy.verbose()
            ParserProxy.verbose()

        if args.cache_folder:
            RequestsProxy.set_cache_folder(args.cache_folder)

        data = self.__get_lyrics_data_by_user_input(args.cnt)

        self.model.fit(data['lyrics'], data['artist'])

        # The command is ready, ask for user for lyrics input
        print('Command is ready')
        while True:
            fragment = input('Enter song fragment: ')
            prediction, prediction_probability = self.model.predict(fragment)
            print('Artist: %s' % prediction)
            print('Prediction probability: ', prediction_probability)
            continue_ = input('Do you want to continue? ("exit" for quit, "enter" for continue.) ')
            if continue_ == 'exit':
                print('Bye!')
                break

    @staticmethod
    def __get_args():
        parser = argparse.ArgumentParser(
            description="Command that scraps lyrics from lyrics.com and predicts artist by song fragment",
            epilog='Example of usage: python3 artist_predictor.py'
        )

        parser.add_argument('--cnt', help='load only N songs per artist', type=int)
        parser.add_argument('-c', '--cache-folder', help='path to the cache folder')
        parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')

        return parser.parse_args()

    def __get_lyrics_data_by_user_input(self, limit_cnt):

        lyrics = []
        artists = []
        artists_cnt = 0

        while True:

            # Enter artist
            try:
                artist_name = input('Enter artist name: ')
                artist_url = self.scraper.get_artist_url(artist_name)
            except Exception as e:
                print(e)
                if input('Continue? ("exit" to quit)) ') == 'exit':
                    sys.exit('Bye!')
                else:
                    continue

            # Search artist and get its list of songs
            try:
                lyrics_url_by_song = self.scraper.get_lyrics_url_by_song_dict(artist_url)
            except Exception as e:
                print(e)
                if input('Continue? ("exit" to quit, "Enter" to enter more artists)) ') == 'exit':
                    sys.exit('Bye!')
                else:
                    continue

            # Go through artist's songs and pull lyrics
            current_cnt = 0
            for song_name, url in tqdm(lyrics_url_by_song.items()):
                try:
                    lyrics = self.scraper.parse_lyrics(url)
                except Exception as e:  # catch *all* exceptions
                    print('Cannot get "%s" from %s (%s)' % (song_name, url, str(e)))
                    continue

                lyrics.append(Model.clean_lyrics(lyrics))
                artists.append(artist_name)

                current_cnt += 1

                if limit_cnt is not None and current_cnt >= limit_cnt:
                    break

            artists_cnt += 1

            prompt = 'Continue? ("yes" to enter more artists, "enter" for moving forward)'
            if artists_cnt > 1 and input(prompt) != 'yes':
                break

        lyrics = pd.Series(lyrics, name='lyrics')
        artists = pd.Series(artists, name='artist')

        return pd.concat([lyrics, artists], axis=1)


if __name__ == '__main__':
    np.random.seed(42)
    Command().exec()
