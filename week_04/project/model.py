from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import LogisticRegression
import re
import pandas as pd


class Model:

    def __init__(self):
        self.pipeline = Pipeline([
            ('tf-idf', TfidfVectorizer(stop_words='english', min_df=4)),
            ('LR', LogisticRegression())
        ])

    @staticmethod
    def clean_lyrics(text: str) -> str:
        text = re.sub(r'[!\.,\'",;\(\)]', '', text)
        text = text.lower()

        tokens = TreebankWordTokenizer().tokenize(text=text)
        tokens = [WordNetLemmatizer().lemmatize(token) for token in tokens]
        tokens = [token for token in tokens if len(token) > 3]

        return " ".join(tokens)

    def fit(self, X, y):
        self.pipeline.fit(X, y)
        d = self.pipeline['tf-idf'].transform(X)
        print(pd.DataFrame(d.toarray(), columns=self.pipeline['tf-idf'].get_feature_names()))

    def predict(self, fragment):
        fragment = Model.clean_lyrics(fragment)
        print('Fragment for prediction: %s' % fragment)
        return self.pipeline.predict([fragment]), self.pipeline.predict_proba([fragment])
