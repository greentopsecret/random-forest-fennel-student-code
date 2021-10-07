from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd

from sklearn.preprocessing import FunctionTransformer


# Inspired by / copy-pasted from https://towardsdatascience.com/pipelines-custom-transformers-in-scikit-learn-ef792bbb3260
# class CustomAgeImputer(BaseEstimator, TransformerMixin):
#     def __init__(self):
#         super().__init__()
#         self.age_means_ = {}
#
#     def fit(self, X, y=None):
#         print(X)
#         self.age_means_ = X[].groupby(['Pclass', 'Sex']).Age.mean()
#
#         return self
#
#     def transform(self, X, y=None):
#         # fill Age
#         for key, value in self.age_means_.items():
#             X.loc[((np.isnan(X["Age"])) & (X.Pclass == key[0]) & (X.Sex == key[1])), 'Age'] = value
#
#         return X

def age_by_group(df):
    # print(df)
    # print(df['Age'].isna().sum())
    df.groupby(by=['Sex', 'Pclass'])
    df.groupby(by=['Sex', 'Pclass'])['Age']
    df.loc[df['Age'].isna(), 'Age'] = df.groupby(by=['Sex', 'Pclass'])['Age'].transform('mean')
    # print(df)
    # print(df['Age'].isna().sum())
    return df


def cabin_to_deck(df):
    df['Cabin'] = df[df['Cabin'].notna()]['Cabin'].astype(str).str[0]
    return df


def main():
    df = pd.read_csv("../data/train.csv", sep=",")
    X = df[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'Cabin']]
    y = df['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)

    # age_pipeline = make_pipeline(
    #     # impute the missing values in the Age column
    #     SimpleImputer(strategy='median'),
    #     # bin the imputed Age column into 3 bins (young, middle-aged, old)
    #     KBinsDiscretizer(n_bins=3, strategy='quantile')
    # )

    pipeline = make_pipeline(
        FunctionTransformer(age_by_group),
        ColumnTransformer([
            ('quantile_age', KBinsDiscretizer(n_bins=3, strategy='quantile'), ['Age']),
            ('ohe_embarked', OneHotEncoder(sparse=False, handle_unknown='ignore'), ['Embarked', 'Sex']),
            ('scale_fare', MinMaxScaler(), ['Fare']),
            ('cabin_to_deck', FunctionTransformer(cabin_to_deck), ['Cabin'])
        ], remainder='passthrough'),
        # ColumnTransformer([
        #     # ('ohe_deck', OneHotEncoder(sparse=False, handle_unknown='ignore'), ['Deck'])
        # ], remainder='passthrough')
    )

    pipeline.fit(X_train)
    X_train_fe = pipeline.transform(X_train)
    X_test_fe = pipeline.transform(X_test)

    # transformer = ColumnTransformer([
    #
    #     # ('age_by_group', FunctionTransformer(age_by_group), ['Age', 'Pclass', 'Sex']),
    #
    #     # impute the missing values in the Age column
    #     ('fillna_and_split_age', age_pipeline, ['Age']),
    #
    #     # one-hot-encode the Embarked column
    #     ('ohe_embarked', OneHotEncoder(sparse=False, handle_unknown='ignore'), ['Embarked', 'Sex']),
    #
    #     # scale the Fare column
    #     ('scale_fare', MinMaxScaler(), ['Fare'])
    #
    # ], remainder='passthrough')
    #
    # transformer.fit(X_train)
    # X_train_fe = transformer.transform(X_train)
    # X_test_fe = transformer.transform(X_test)

    # instantiate the model
    m = LogisticRegression()
    # train the model
    m.fit(X_train_fe, y_train)
    # score train data
    print('score train data: %0.4f' % m.score(X_train_fe, y_train))
    # score test data
    print('score test data: %0.4f' % m.score(X_test_fe, y_test))


if __name__ == '__main__':
    main()
