# /usr/local/bin/python3 /Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/command.py

from parser import Parser
from tqdm import tqdm
import numpy as np
import pandas as pd
import sys
import re
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import LogisticRegression
from requests_proxy import RequestsProxy


class Command:

    def __init__(self):
        self.requests = RequestsProxy()
        self.parser = Parser()

    def exec(self):
        args = self.__get_args()
        if args.verbose:
            self.requests.verbose()

        X, y = self.__get_lyrics_data(args.cnt)
        pipeline = self.__prepare_pipeline(X, y)
        self.__run_predictions(pipeline)

    def __get_args(self):
        parser = argparse.ArgumentParser(
            description="Command that scraps lyrics from lyrics.com and predicts artist by song fragment",
            epilog='Example of usage: /usr/local/bin/python3 /Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/command.py'
        )

        parser.add_argument('--cnt', help='load only N songs per artist', type=int)
        parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')

        return parser.parse_args()

    def __clean_lyrics(self, text: str) -> str:
        text = re.sub(r'[!\.,\'",;\(\)]', '', text)
        text = text.lower()

        tokens = TreebankWordTokenizer().tokenize(text=text)

        return " ".join(WordNetLemmatizer().lemmatize(token) for token in tokens)

    def __get_artist_url(self, artist_name: str) -> str:
        html = self.requests.get('https://www.lyrics.com/lyrics/%s' % artist_name)
        return 'https://www.lyrics.com/' + self.parser.parse_artist_url(html, artist_name)

    def __get_lyrics_data(self, cnt):

        X = []
        y = pd.Series(dtype=int)

        while True:

            # Enter artist
            try:
                artist_name = input('Enter artist name: ')
                artist_url = self.__get_artist_url(artist_name)
            except Exception as e:
                print(e)
                if input('Continue? ("n" to quit)) ') == 'n':
                    sys.exit('Bye!')
                else:
                    continue

            # Search artist and get it's list of songs
            try:
                html = self.requests.get(artist_url)
                lyrics_url_by_song = self.parser.get_lyrics_url_by_song_dict(html)
            except Exception as e:
                print(e)
                if input('Continue? ("n" to quit, "Enter" to enter more artists)) ') == 'n':
                    sys.exit('Bye!')
                else:
                    continue

            # Go through artist's songs and pull lyrics
            corpus = []
            for song_name, url in tqdm(lyrics_url_by_song.items()):

                try:
                    lyrics = self.parser.parse_lyrics(self.requests.get('https://www.lyrics.com/' + url))
                except Exception as e:  # catch *all* exceptions
                    print('Cannot get "%s" from %s (%s)' % (song_name, url, str(e)))
                    continue

                corpus.append(self.__clean_lyrics(lyrics))

                if cnt is not None and len(corpus) >= cnt:
                    break

            X = X + corpus
            y = y.append(pd.Series(artist_name).repeat(len(corpus)), ignore_index=True)

            if y.unique().size > 1 and input(
                    'Continue? ("y" to enter more artists, "enter" for moving forward)') != 'yes':
                break

        return X, y

    def __prepare_pipeline(self, X, y):
        # Prepare pipeline
        pipeline = Pipeline([
            ('tf-idf', TfidfVectorizer(stop_words='english', min_df=5)),
            ('LR', LogisticRegression())
        ])
        return pipeline.fit(X, y)

    def __run_predictions(self, pipeline: Pipeline):
        # The command is ready, ask for user for lyrics input
        print('Command is ready')
        while True:
            fragment = self.__clean_lyrics(input('Enter song fragment: '))
            print('Artist: %s' % pipeline.predict([fragment]))
            print('Prediction probability: ', pipeline.predict_proba([fragment]))
            continue_ = input('Do you want to continue? ("n" for quit, "enter" for continue.) ')
            if continue_ == 'n':
                print('Bye!')
                break


if __name__ == '__main__':
    np.random.seed(42)
    Command().exec()
