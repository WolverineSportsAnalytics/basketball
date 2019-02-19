import mysql.connector
import pca_step1_modelworkflow

import sklearn

from sklearn.linear_model import LinearRegression, Ridge, Lasso

from sklearn.preprocessing import scale

import numpy as np

from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score, mean_absolute_error

import pandas as pd

import models
from sklearn.decomposition import PCA

from sklearn.preprocessing import normalize


def train_model():
    '''trains a model on PCA-reduced data and tunes the hyperparameters. Returns the model'''
    cnx = mysql.connector.connect(user="root",

                                  host="127.0.0.1",

                                  database="basketball",

                                  password="Federer123!")
    cursor = cnx.cursor(buffered=True)

    # extract features from database
    features = pca_step1_modelworkflow.get_features_matrix(cnx, cursor, 0, 900)

    # get features and response variable
    features, response = pca_step1_modelworkflow.split_features(features, np.linspace(
        0, 455, dtype=int, num=455))  # 456 relevant features after removal of fanduel and draftkings

    # run pca to get sparse representation of data
    features_train = features[:14000]
    response_train = response[:14000]
    features_test = features[14000:]
    response_test = response[14000:]
    features_train_pca, features_test_pca = pca_step1_modelworkflow.run_pca(
        features_train, features_test)

    # Run Ridge without Feature Selection to get Variable Importance

    # train model with different alphas

    '''mses = [];
    progression = [0.001*10**i for i in range(7)]
    for my_alpha in progression:
        model = Ridge(alpha=my_alpha);
        model.fit(features_train, response_train);

        y_pred1 = model.predict(features_test) #test prediction
        mses.append(mean_squared_error(response_test, y_pred1))

    print progression
    print mses'''


def cross_validation(clf, train_x, train_y, k):
    '''

    Takes in a model with set hyperperameters and train_x and train_y

    Will run k fold cross validation and return perfomance metrics (r2)

    can take in any model

    '''

    k_fold = KFold(5, shuffle=True)

    scores = cross_val_score(
        clf,
        train_x,
        train_y,
        cv=k_fold,
        n_jobs=1,
        scoring='neg_mean_squared_error')

    return scores


def main():

    train_model()


if __name__ == "__main__":

    main()
