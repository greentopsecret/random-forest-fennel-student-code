FROM python:3.6-slim

WORKDIR /tweet_collector

COPY requirements.txt /tweet_collector
RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "get_tweets.py"]
