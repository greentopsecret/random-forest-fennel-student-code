import json
import logging
import pandas as pd
import numpy as np
import os

FILE_PATH = os.path.dirname(__file__)


def get_cosim(X, Y):
    num = np.nansum(X * Y)  # np.dot(X, Y)
    denom = np.sqrt(np.nansum(X * X) * np.nansum(Y * Y))  # np.sqrt(np.dot(X, X)) * np.sqrt(np.dot(Y, Y))
    return num / denom


def find_movies_by_title(movies, movie_titles):
    return pd.DataFrame(movie_titles, columns=['title']).merge(movies, how='inner', on='title')


def find_users_id_by_movies(movies, ratings):
    m = movies.copy()
    m = m.merge(ratings, how='inner', on='movieId')
    m['cnt'] = 1
    s = m.groupby(by='userId')['cnt'].sum()

    # take only users who watched more than 40% of movies from the list
    return s[s.sort_values() > len(movies) * 0.4].index.tolist()


def filter_ratings(reference_users_id, input_movies, ratings):
    return ratings[(ratings['userId'].isin(reference_users_id)) &
                   (ratings['movieId'].isin(input_movies['movieId'])) &
                   (ratings['rating'] >= 4)]  # TODO: check results if this filter is removed


def get_recommendations(input_movies: list):
    input_movies = list(x.lower() for x in input_movies)

    data_path = 'data/ml-latest-small'
    movies = pd.read_csv(os.path.join(FILE_PATH, data_path, 'movies.csv'), usecols=['movieId', 'title'])
    ratings = pd.read_csv(os.path.join(FILE_PATH, data_path, 'ratings.csv'), usecols=['movieId', 'userId', 'rating'])

    movies['title_raw'] = movies['title']
    movies['title'] = movies['title_raw'].str.extract(r'([^\()]+)', expand=False).str.lower().str.strip()
    movies['year'] = movies['title_raw'].str.extract(r' \((\d+)\)')

    input_movies = find_movies_by_title(movies, input_movies)
    input_ratings = pd.Series([5] * len(input_movies), index=input_movies['movieId'])

    # find users (reference users) who watched all movies from the input list
    reference_users_id = find_users_id_by_movies(input_movies, ratings)

    ratings_filtered = filter_ratings(reference_users_id, input_movies, ratings)

    df = movies[['movieId', 'title']]. \
        merge(ratings_filtered[['userId', 'movieId', 'rating']], on="movieId"). \
        pivot(columns='movieId', values='rating', index='userId'). \
        transpose()

    cosim_dict = {}
    for reference_user in df.columns:
        cosim_dict[reference_user] = get_cosim(df[reference_user], input_ratings)

    # TODO: use heapq
    cosim_reference_users = pd.DataFrame(cosim_dict.values(), index=cosim_dict.keys(), columns=['cosim'])
    cosim_reference_users.sort_values(inplace=True, by='cosim')
    reference_users_id = cosim_reference_users.tail(10).index.tolist()

    # prepare candidates
    # movies that are not in user input and that have the biggest amount of positive ratings from reference users
    ratings_for_unseen_movies = ratings[(~ratings['movieId'].isin(input_movies['movieId'])) & \
                                        (ratings['userId'].isin(reference_users_id))]
    candidate_movies_id = ratings_for_unseen_movies.groupby('movieId'). \
        agg({'userId': 'count'}). \
        rename(columns={'userId': 'numberOfReviews'}). \
        sort_values('numberOfReviews'). \
        tail(10). \
        index.tolist()

    # prediction: predict ratings for candidate movies
    candidate_predictions = {}
    for candidate_movie_id in candidate_movies_id:
        num = 0
        denom = 0

        for reference_user_id, cosim in cosim_reference_users.tail(100).to_dict()['cosim'].items():
            r = ratings[(ratings['userId'] == reference_user_id) & (ratings['movieId'] == candidate_movie_id)]['rating']
            rating = r.values[0] if len(r) else 0

            num += cosim * rating
            denom += cosim

        candidate_predictions[candidate_movie_id] = num / denom if denom > 0 else 0

    # candidate_predictions = dict(sorted(candidate_predictions.items(), key=lambda item: item[1], reverse=True))
    candidate_predictions = pd.DataFrame(
        list(candidate_predictions.values()),
        index=list(candidate_predictions.keys()),
        columns=['predicted'])
    movies[['title']]. \
        merge(candidate_predictions, left_index=True, right_index=True, how='inner'). \
        sort_values('predicted', ascending=False)

    return movies.head(3)['title'].tolist()


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    logger = logging.getLogger(__name__)
    logger.debug('Got an event: {}' % event)

    if 'body' not in event.keys():
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": 'No "body" provided'
            }),
        }

    body = json.loads(event['body'])
    reference_movies = body['reference_movies']

    return {
        "statusCode": 200,
        "body": json.dumps({
            "recommendations": get_recommendations(reference_movies)
        }),
    }
