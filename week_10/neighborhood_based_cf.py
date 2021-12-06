import pandas as pd
import numpy as np


class NeighborhoodBasedCF:

    def __init__(self, df: pd.DataFrame, min_cosim: float = 0.65, min_reference_users_cnt: int = 3):
        self.df = df.T
        self.min_cosim = min_cosim
        self.min_reference_users_cnt = min_reference_users_cnt

    def predict_ratings(self, target_user: str) -> dict:

        # movies they haven't seen
        isna_user = self.df[target_user].isna()
        unseen_movies = self.df[isna_user].index

        cosim_df = NeighborhoodBasedCF._build_cosim_df(self.df)

        # users that can be used as references
        reference_users = cosim_df[cosim_df[target_user] > self.min_cosim]. \
            loc[NeighborhoodBasedCF._exclude_target_user(target_user)]. \
            index.tolist()

        # for each of the movies they haven't seen, get the list of users who have seen it
        pred_movies = {}
        for movie in unseen_movies:
            num = 0
            denom = 0

            movie_reference_users = self.df.loc[movie, reference_users].dropna()

            if len(movie_reference_users) < self.min_reference_users_cnt:
                continue

            for reference_user, rating in movie_reference_users.items():
                cosim = cosim_df.loc[target_user, reference_user]
                num += cosim * rating
                denom += cosim

            pred_movies[movie] = num / denom if denom > 0 else 0

        return {k: round(v) for k, v in pred_movies.items()}

    @classmethod
    def _build_cosim_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        cosim_table = []
        for user1 in df.columns:
            row = []
            for user2 in df.columns:
                row.append(cls._cosim(df[user1], df[user2]))
            cosim_table.append(row)

        return pd.DataFrame(cosim_table, index=df.columns, columns=df.columns).round(2)

    @staticmethod
    def _cosim(X, Y) -> float:
        num = np.nansum(X * Y)  # np.dot(X, Y)
        denom = np.sqrt(np.nansum(X * X) * np.nansum(Y * Y))  # np.sqrt(np.dot(X, X)) * np.sqrt(np.dot(Y, Y))
        return num / denom

    @classmethod
    def _exclude_target_user(cls, target_user: str):
        return lambda x: x.index != target_user


if __name__ == '__main__':
    df = pd.DataFrame({
        "Movie1": [None, 4, 1, 1, None],
        "Movie2": [3, 4, 1, None, 4],
        "Movie3": [1, 5, None, 2, 1],
        "Movie4": [2, None, None, 1, 1],
        "Movie5": [5, None, 5, 3, 1],
    }, index=['user1', 'user2', 'user3', 'user4', 'user5'])

    r = NeighborhoodBasedCF(df, 0.65, 2)

    assert {'Movie1': 1.0} == r.predict_ratings('user1')
    assert {} == r.predict_ratings('user2')
    assert {'Movie3': 1, 'Movie4': 2} == r.predict_ratings('user3')
    assert {'Movie2': 2} == r.predict_ratings('user4')
    assert {} == r.predict_ratings('user5')
