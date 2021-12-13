'''
The module etl.py extracts twitter data from a MongoDB database, transforms it
and loads it into a PostgreSQL database.
Thanks to Stefan!
'''

import time
import logging
import random
import re
import pymongo
from sqlalchemy import create_engine

# CLIENT = pymongo.MongoClient("mongodb://mongodb:27017/")
CLIENT = pymongo.MongoClient("mongodb")
DB = CLIENT.tweets

DATABASE_UP = False

PG = create_engine('postgres://postgres:1234@postgresdb:5432')
PG.execute('''CREATE TABLE IF NOT EXISTS tweets (
id BIGSERIAL,
text VARCHAR(512),
sentiment NUMERIC
);
''')


### we could try and wait for a database connection to be established before continuing, the below code achieves this
# while not DATABASE_UP:
# try:
#     PG = create_engine('postgres://postgres:1234@postgresdb:5432')
#     PG.execute('''CREATE TABLE IF NOT EXISTS tweets (
#     text VARCHAR(512),
#     sentiment NUMERIC
#     );
#     ''')
#     DATABASE_UP = True
# except exc.OperationalError:
#     time.sleep(1)
#     continue


def extract():
    """gets a random tweet"""
    tweets = list(DB.collections.data_science.find())
    if tweets:
        t = random.choice(tweets)
        logging.critical("random tweet: " + t['text'])
        return t


def transform(tweet):
    # here we will insert the sentiment analysis results
    text = re.sub("'", "", tweet["text"])
    sentiment = 1
    logging.critical("sentiment: " + str(sentiment))
    return [text, sentiment]


def load(tweet, sentiment):
    PG.execute(f"""INSERT INTO tweets (text, sentiment) VALUES ('''{tweet}''', {sentiment});""")
    logging.critical("tweet + sentiment written to PG")


# here we will define an Airflow task

logging.critical("Hello from the ETL job")

while True:
    tweet = extract()
    if tweet:
        result = transform(tweet)
        load(result[0], result[1])
    time.sleep(10)
