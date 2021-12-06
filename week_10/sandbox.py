import pandas as pd
import numpy as np
import math


def _strip(x):
    return x.strip()


def cosim(X, Y):
    num = np.nansum(X * Y)  # np.dot(X, Y)
    denom = np.sqrt(np.nansum(X * X) * np.nansum(Y * Y))  # np.sqrt(np.dot(X, X)) * np.sqrt(np.dot(Y, Y))
    return num / denom


if __name__ == '__main__':
    df = pd.read_csv('./data/RFFMovieRatings.csv', index_col=0)

    df.rename(columns=_strip, index=_strip, inplace=True)
    df.columns.tolist(), df.index.tolist()
    df = df.T

    cosim_table = []
    for user1 in df.columns:
        row = []
        for user2 in df.columns:
            row.append(cosim(df[user1], df[user2]))
        cosim_table.append(row)

    cosim_df = pd.DataFrame(cosim_table, index=df.columns, columns=df.columns).round(2)

    # recomender parameters
    min_cosim = 0.65
    min_reference_users_cnt = 3

    # target user
    target_user = 'Maxim'

    # movies they haven't seen
    isna_user = df[target_user].isna()
    unseen_movies = df[isna_user].index

    # users that can be used as references
    exclude_target_user = lambda x: x.index != target_user
    reference_users = cosim_df[cosim_df[target_user] > min_cosim].loc[exclude_target_user].index.tolist()

    # for each of the movies they haven't seen, get the list of users who have seen it
    pred_movies = {}
    for movie in unseen_movies:
        num = 0
        denom = 0

        movie_reference_users = df.loc[movie, reference_users].dropna()

        if len(movie_reference_users) < min_reference_users_cnt:
            continue

        print(movie_reference_users)

        for reference_user, rating in movie_reference_users.items():

            cosim = cosim_df.loc[target_user, reference_user]
            num += cosim * rating
            denom += cosim

        print('movie: %s; num: %s; denom: %s; reference_users_cnt: %d' % (movie, num, denom, len(reference_users)))

        pred_movies[movie] = num / denom if denom > 0 else 0

    print(pred_movies)
