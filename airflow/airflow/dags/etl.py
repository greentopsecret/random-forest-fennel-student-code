'''
This is our first dag.
'''
##### 1. import modules #####
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import logging
import pymongo
import random
import re
from sqlalchemy import create_engine, exc

# import more libraries

##### 1.b) create connections #####
CLIENT = pymongo.MongoClient("mongodb")
DB = CLIENT.tweets

PG = create_engine('postgres://postgres:postgres@postgresdb2:5432')
PG.execute('''CREATE TABLE IF NOT EXISTS tweets (
id BIGSERIAL,
text VARCHAR(512),
sentiment NUMERIC
);
''')


##### 1.c) create python_callables #####
def extract():
    """gets a random tweet"""
    tweets = list(DB.collections.data_science.find())
    if tweets:
        t = random.choice(tweets)
        logging.critical("random tweet: " + t['text'])
        return t


def transform(**context):
    # here we will insert the sentiment analysis results
    extract_connection = context['task_instance']
    tweet = extract_connection.xcom_pull(task_ids="extract")
    text = re.sub("'", "", tweet["text"])
    sentiment = 1
    logging.critical("sentiment: " + str(sentiment))
    result = [text, sentiment]
    return result


def load(**context):
    extract_connection = context['task_instance']
    result = extract_connection.xcom_pull(task_ids="transform")
    tweet, sentiment = result[0], result[1]
    PG.execute(f"""INSERT INTO tweets (text, sentiment) VALUES ('''{tweet}''', {sentiment});""")
    logging.critical("tweet + sentiment written to PG")


def slack_message():
    ...


##### 2. define default arguments #####
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 4, 1),
    # 'end_date':
    'email': ['stefan@spiced-academy.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}

##### 3. instantiate a DAG #####
dag = DAG('etl', description='', catchup=False, schedule_interval=timedelta(minutes=1), default_args=default_args)

##### 4. create the tasks #####
t1 = PythonOperator(task_id='extract', python_callable=extract, dag=dag)

t2 = PythonOperator(task_id='transform', provide_context=True, python_callable=transform, dag=dag)

t3 = PythonOperator(task_id='load', provide_context=True, python_callable=load, dag=dag)

t4 = PythonOperator(task_id='slackbot', python_callable=slack_message, dag=dag)

##### 5. Set up dependencies #####
t1 >> t2 >> t3 >> t4
