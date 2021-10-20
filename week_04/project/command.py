
# /usr/local/bin/python3 /Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_04/project/command.py \
#   -a 'https://www.lyrics.com/artist.php?name=The-Frames&aid=21708&o=1' \
#   -a 'https://www.lyrics.com/artist.php?name=Guano-Apes&aid=295621&o=1' \
#   -a 'https://www.lyrics.com/artist.php?name=Michael-Jackson&aid=4576&o=1' \
#   -a 'https://www.lyrics.com/artist.php?name=Modern-Talking&aid=141630&o=1' \
#   --cnt=100

import argparse, requests, re
from bs4 import BeautifulSoup
from scraper_proxy import ScraperProxy
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

np.random.seed(42)

def get_args():
    parser = argparse.ArgumentParser(
        description="Command that scraps lyrics from an external source",
        epilog='Example'
    )
    
    # parser.add_argument('-a', '--artist', help='Artist\'s name', required=True) # TODO: handle artist name
    # parser.add_argument('-???', '--???', help='') # TODO: handle hyperparameters
    parser.add_argument('-a', '--artist-url', help='url to artist\' list of songs', action='append', required=True)
    # parser.add_argument('--refresh-cache', help='refresh cache files', default=False) # TODO: handle this parameter
    parser.add_argument('--cnt', help='process only N first songs', type=int)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', help='verbose output', default=False)
    group.add_argument('-q', '--quiet', help='no output', default=False)

    return parser.parse_args()

# incoming/outcomming parameters type
def get_lyrics_urn_by_song_dict(html):
    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find('table', class_='tdata').find('tbody').find_all('tr'):
        link = tr.find_all('td')[0].find('a')
        song_name = link.text.lower()
        song_name = re.sub(r'[,\.:\'"]', '', song_name)
        song_name = re.sub(r'\[[\w -]+\]', '', song_name) # remove strings like "[live]" or "[immortal version]"
        song_name = song_name.strip()
        result[song_name] = link.attrs['href']

    return result

def parse_lyrics_html(html):
    body = BeautifulSoup(html, 'html.parser').find(id='lyric-body-text')
    if not body:
        raise Exception('No song found')
    return body.text

# def clean_lyrics(text: str):
#     text = text.lower()
#     return text

def clean_lyrics(text):
    text = re.sub(r'[!\.,\'",;\(\)]', '', text)
    text = text.lower()

    tokenizer = TreebankWordTokenizer()
    lemmatizer = WordNetLemmatizer()

    tokens = tokenizer.tokenize(text=text)

    return " ".join(lemmatizer.lemmatize(token) for token in tokens)

def main():
    args = get_args()
    # TODO: handle "--refresh-cache" option

    scriper = ScraperProxy()
    parser = Parser()

    X = []
    y = pd.Series(dtype=int)
    for i, artist_url in enumerate(args.artist_url):

        # url = 'https://www.lyrics.com/artist.php?name=Guano-Apes&aid=295621&o=1'
        domain = '/'.join(artist_url.split('/')[0:3])

        html = scriper.get_songs_list_html(artist_url)
        lyrics_urn_by_song = get_lyrics_urn_by_song_dict(html)

        # print(lyrics_urn_by_song)

        corpus = []
        for song_name, urn in tqdm(lyrics_urn_by_song.items()):
            
            # scriper.get_lyrics_html(domain + urn)
            try:
                url = domain + urn
                lyrics = parse_lyrics_html(scriper.get_lyrics_html(url))
            except Exception as e: # catch *all* exceptions
                print('Cannot get "%s" from %s (%s)' % (song_name, url, str(e)))
                continue

            corpus.append(clean_lyrics(lyrics))

            # corpus.append(lyrics)

            if args.cnt is not None and len(corpus) >= args.cnt:
                break

        X = X + corpus
        y = y.append(pd.Series(i).repeat(len(corpus)), ignore_index=True)
        



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # pipe = Pipeline([
    #     ('count', CountVectorizer(stop_words=stopwords.words('english'), min_df=1)),
    #     ('tfid', TfidfTransformer())
    # ]).fit(X_train)


    # pipe = Pipeline([
    #     TfidfVectorizer(stop_words='english'),
    # ]).fit(X_train)

    # print(X_train)

    vectorizer = TfidfVectorizer(stop_words='english', min_df=5)
    vectorizer.fit(X_train, y_train)

    X_train_fe = vectorizer.transform(X_train).toarray()
    X_test_fe = vectorizer.transform(X_test).toarray()

    # clf = GaussianNB()
    # clf.fit(X_train_fe, y_train)

    clf = RandomForestClassifier(max_depth=5)
    clf.fit(X_train_fe, y_train)
    
    y_pred = clf.predict(X_test_fe)
    y_train_pred = clf.predict(X_train_fe)

    scores = pd.DataFrame([
        [accuracy_score(y_train, y_train_pred), accuracy_score(y_test, y_pred)],
        [f1_score(y_train, y_train_pred, average='weighted'), f1_score(y_test, y_pred, average='weighted')],
        [precision_score(y_train, y_train_pred, average='weighted'), precision_score(y_test, y_pred, average='weighted')],
    ], index=['accuracy', 'f1', 'precision'], columns=['train', 'test'])
    print(scores)

    # # 'accuracy_score (train data): %.4f; accuracy_score (test data): %.4f' % (rmslr(y_train, y_pred_train), rmslr(y_test, y_pred))

    # # print(X_train_fe)

    # X_train_fe = pd.DataFrame(X_train_fe, columns=vectorizer.get_feature_names_out())
    # X_test_fe = pd.DataFrame(X_test_fe, columns=vectorizer.get_feature_names_out())
    
    # print(X_train_fe)
    # print(vectorizer.get_feature_names_out())

    

    

if __name__ == '__main__':
    main()