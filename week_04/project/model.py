from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import LogisticRegression
import re


class Model:

    def __init__(self):
        self.pipeline = Pipeline([
            ('tf-idf', TfidfVectorizer(stop_words='english', min_df=5)),
            ('LR', LogisticRegression())
        ])

    @staticmethod
    def clean_lyrics(text: str) -> str:
        text = re.sub(r'[!\.,\'",;\(\)]', '', text)
        text = text.lower()

        tokens = TreebankWordTokenizer().tokenize(text=text)

        return " ".join(WordNetLemmatizer().lemmatize(token) for token in tokens)

    def fit(self, X, y):
        self.pipeline.fit(X, y)

    def predict(self, fragment):
        fragment = Model.clean_lyrics(fragment)
        return self.pipeline.predict([fragment]), self.pipeline.predict_proba([fragment])
