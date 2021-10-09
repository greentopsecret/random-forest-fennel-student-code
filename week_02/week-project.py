# TODO: explore data
#   X Calculate the number of surviving/non-surviving passengers and display it as a bar plot.
#   x Create a bar plot with separate bars
#   x   for male/female passengers
#   x   1st/2nd/3rd class passengers.
#   Calculate the proportion of surviving 1st class passengers with regards to the total number of 1st class passengers.
#   Create a histogram showing the age distribution of passengers. Compare surviving/non-surviving passengers.
#   Calculate the average age for survived and drowned passengers separately.
#   Pairs plot (with color=survived)
# TODO: Feature engineering:
#   X   Add "Pclass"
#   X   Add "Parch" (for some reasons it decreases accuracy)
#   X   Add "Cabin"
#   X   One column for siblings-num
#   X One column for fare
#   X MinMaxScaler for fare
#   Add column names
# TODO: Decision Tree - plot - https://krspiced.pythonanywhere.com/chapters/project_titanic/random_forests/decision_trees.html
# TODO:
#   Random Forests - https://krspiced.pythonanywhere.com/chapters/project_titanic/random_forests/random_forests.html#random-forest
#       Feature importance
# TODO: Evaluation
#     Confusion matrix: add labels
#     Cross validation: apply woth accuracy, precision and recall - https://krspiced.pythonanywhere.com/chapters/project_titanic/cross_validation/README.html#crossval
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split


# def process_sibsp(df: pd.DataFrame):
# #     SibSp
# #     Parch
#     df.loc[(df['SibSp']) >= 5, 'SibSp_tmp'] = 'XL'
#     df.loc[(df['SibSp']) >= 3 & (df['SibSp'] < 5), 'SibSp_tmp'] = 'L'
#     df.loc[(df['SibSp']) >= 1 & (df['SibSp'] < 3), 'SibSp_tmp'] = 'M'
#     df.loc[(df['SibSp']) == 0, 'SibSp_tmp'] = 'S'
#
#     df['SibSp'] = df['SibSp_tmp']
#     df.drop(columns='SibSp_tmp')
#
#     return df.copy(deep=True)

def cabin_to_deck(df: pd.DataFrame) -> pd.DataFrame:
    df['Cabin'] = df['Cabin'].str[0].map({'A': 1,
                                          'B': 2,
                                          'C': 3,
                                          'D': 4,
                                          'E': 5,
                                          'F': 6,
                                          'G': 7,
                                          'T': 8,
                                          'Z': 9,
                                          np.NAN: 9})

    return df


def main():
    df = pd.read_csv("../data/train.csv", sep=",")

    X = df[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'Cabin', 'Name']]
    y = df['Survived']
    X_train, X_test, y_train_true, y_test_true = train_test_split(X, y, test_size=0.2, random_state=151)

    age_pipeline = make_pipeline(
        SimpleImputer(strategy='mean'),
        KBinsDiscretizer(n_bins=3, encode='onehot-dense', strategy='quantile')
    )
    fare_pipeline = make_pipeline(
        SimpleImputer(strategy='mean'),
        MinMaxScaler()
    )
    # sibsp_pipeline = make_pipeline(
    #     FunctionTransformer(process_sibsp),
    #     OneHotEncoder(sparse=False, handle_unknown='ignore')
    # )

    pipeline = ColumnTransformer([
        ('age_transformer', age_pipeline, ['Age']),
        ('sex_transformer', OneHotEncoder(sparse=False, handle_unknown='ignore'), ['Sex']),
        ('fare_transformer', fare_pipeline, ['Fare']),
        ('cabin_transformer', FunctionTransformer(cabin_to_deck), ['Cabin']),
        # ('family_transformer', sibsp_pipeline, ['SibSp']),
        ('pass_through', 'passthrough', ['Pclass', 'SibSp']),
    ], remainder='drop')

    pipeline.fit(X_train)
    X_train_fe = pipeline.transform(X_train)
    X_test_fe = pipeline.transform(X_test)

    m = LogisticRegression()
    m.fit(X_train_fe, y_train_true)

    y_test_pred = m.predict(X_test_fe)

    print("precision_score: %.4f" % metrics.accuracy_score(y_test_true, y_test_pred))
    print("precision_score: %.4f" % metrics.precision_score(y_test_true, y_test_pred))
    print("recall_score: %.4f" % metrics.recall_score(y_test_true, y_test_pred))
    print("f1_score: %.4f" % metrics.f1_score(y_test_true, y_test_pred))


if __name__ == '__main__':
    main()
