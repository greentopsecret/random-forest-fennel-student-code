# /usr/local/bin/python3 /Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/command.py

import argparse, re
from requests_proxy import RequestsProxy
from parser import Parser
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
import numpy as np
import nltk
from nltk.corpus import stopwords
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score
import sys
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import LogisticRegression

class Command():

    def exec():
        args = Command.get_args()
        if args.verbose:
            RequestsProxy.verbose()

        X, y = Command.__get_lyrics_data(args.cnt)
        pipeline = Command.__prepare_pipeline(X, y)
        Command.__run_predictions(pipeline)

    def get_args():
        parser = argparse.ArgumentParser(
            description="Command that scraps lyrics from an external source",
            epilog='Example of usage: /usr/local/bin/python3 /Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/command.py'
        )

        parser.add_argument('--cnt', help='load only N songs per artist', type=int)
        parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')

        return parser.parse_args()

    def clean_lyrics(text):
        text = re.sub(r'[!\.,\'",;\(\)]', '', text)
        text = text.lower()

        tokenizer = TreebankWordTokenizer()
        lemmatizer = WordNetLemmatizer()

        tokens = tokenizer.tokenize(text=text)

        return " ".join(lemmatizer.lemmatize(token) for token in tokens)

    def get_artist_url(artist_name):
        html = RequestsProxy.get('https://www.lyrics.com/lyrics/%s' % artist_name)
        return 'https://www.lyrics.com/' + Parser.parse_artist_url(html, artist_name)

    def __get_lyrics_data(cnt):

        X = []
        y = pd.Series(dtype=int)

        while True:

            # Enter artist
            try:
                artist_name = input('Enter artist name: ')
                artist_url = Command.get_artist_url(artist_name)
            except Exception as e:
                print(e)
                if input('Continue? ("n" to quit)) ') == 'n':
                    sys.exit('Bye!')
                else:
                    continue

            # Search artist and get it's list of songs
            try:
                html = RequestsProxy.get(artist_url)
                lyrics_url_by_song = Parser.get_lyrics_url_by_song_dict(html)
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
                    lyrics = Parser.parse_lyrics(RequestsProxy.get('https://www.lyrics.com/' + url))
                except Exception as e: # catch *all* exceptions
                    print('Cannot get "%s" from %s (%s)' % (song_name, url, str(e)))
                    continue

                corpus.append(Command.clean_lyrics(lyrics))

                if cnt is not None and len(corpus) >= cnt:
                    break

            X = X + corpus
            y = y.append(pd.Series(artist_name).repeat(len(corpus)), ignore_index=True)

            if y.unique().size > 1 and input('Continue? ("y" to enter more artists, "enter" for moving forward)') != 'yes':
                break

        return X, y

    def __prepare_pipeline(X, y):
        # Prepare pipeline
        pipeline = Pipeline([
            ('tf-idf', TfidfVectorizer(stop_words='english', min_df=5)),
            ('LR', LogisticRegression())
        ])
        return pipeline.fit(X, y)

    def __run_predictions(pipeline):
        # The command is ready, ask for user for lyrics input
        print('Command is ready')
        while True:
            fragment = Command.clean_lyrics(input('Enter song fragment: '))
            print('Artist: %s' % pipeline.predict([fragment]))
            print('Prediction probability: ', pipeline.predict_proba([fragment]))
            continue_ = input('Do you want to continue? ("n" for quit, "enter" for continue.) ')
            if continue_ == 'n':
                print('Bye!')
                break

if __name__ == '__main__':
    np.random.seed(42)
    Command.exec()