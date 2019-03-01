

import mysql.connector

import sklearn

from sklearn.linear_model import LinearRegression, Ridge, Lasso

from sklearn.preprocessing import scale

import numpy as np

from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score, mean_absolute_error

import pandas as pd

import models
from sklearn.decomposition import PCA

from sklearn.preprocessing import normalize


def get_features_from_model(model, dateID, cursor):

    getFeatures = "SELECT "

    for m in (model):

        getFeatures += m

        getFeatures += ", "

    getFeatures = getFeatures[:-2]

    getFeatures += " FROM futures"    # turn into numpy arrays

    getFeatures += " WHERE dateID < "

    getFeatures += str(dateID)

    print getFeatures

    cursor.execute(getFeatures)

    return cursor.fetchall()


def get_features_matrix(cnx, cursor, start_date, end_date):
    '''

    Will connect to database and get all the features for all players in between

    start_date and end_date, which are date id's

    Returns matrix of all players, their features, and final performance (fanduel points scored)

    '''

    select = "Select * from futures where dateID > %s and dateID < %s and fanduelPts>10"

    days = (start_date, end_date)

    cursor.execute(select, days)

    features_tuples = cursor.fetchall()

    return [list(feature) for feature in features_tuples]


def test_pca(X_train, X_test, Y_train, Y_test):
    '''applies Principal Component Analysis on data, with varying number of components to find the optimal number'''
    '''201 components combined with Ridge regression seems to be optimal'''
    r_squared_train = []
    r_squared_test = []
    comprange = range(1, 440, 20)

    for comp in comprange:

        pca = PCA(n_components=comp)
        pca.fit(X_train)
        X_train_pca = pca.transform(X_train)
        X_test_pca = pca.transform(X_test)

        new_model = Ridge()
        new_model.fit(X_train_pca, Y_train)
        y_pred1 = new_model.predict(X_train_pca)  # train prediction
        y_pred2 = new_model.predict(X_test_pca)  # test prediction

        r_squared_train.append(mean_squared_error(Y_train, y_pred1))

        r_squared_test.append(mean_squared_error(Y_test, y_pred2))

    print comprange
    print r_squared_train
    print r_squared_test


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


def split_features(featuresMatrix, chosenFeatures):
    '''

    Takes a matrix of features and a list of indices (chosen features)

    to take all the features from the futures table and slim them to

    only the features we want to train on and evaluate



    returns new featuresMatrix with only the chosenFeatures

    '''

    # first, remove the draft_kings points (not needed)

    draft_kings = [features.pop(-1) for features in featuresMatrix]

    # extract and remove the fanduel points (response variable)

    fanduel = [features.pop(-1) for features in featuresMatrix]

    featuresMatrix = scale(featuresMatrix)

    # return only the chosen features from features table, and the fanduel
    # points

    return featuresMatrix[:, chosenFeatures], fanduel


def main():

    cnx = mysql.connector.connect(user="root",

                                  host="127.0.0.1",

                                  database="basketball",

                                  password="Federer123!")
    cursor = cnx.cursor(buffered=True)

    # extract features from database
    features = get_features_matrix(cnx, cursor, 0, 900)

    # get features and response variable
    # 456 relevant features after removal of fanduel and draftkings
    features, response = split_features(
        features, np.linspace(
            0, 455, dtype=int, num=455))

    # split into training and testing sets
    features_train = features[:14000]

    response_train = response[:14000]

    features_test = features[14000:]

    response_test = response[14000:]

    # Run Ridge without Feature Selection to get Variable Importance
    model = Ridge()

    # train model
    model.fit(features_train, response_train)

    y_pred1 = model.predict(features_train)  # train prediction

    y_pred2 = model.predict(features_test)  # test prediction

    # print "MLP RELU", hidden_layer

    print "Ridge Regressor"

    print "Feature Selection Method: None"

    r_squared_train = mean_squared_error(response_train, y_pred1)

    r_squared_test = mean_squared_error(response_test, y_pred2)

    print features_train.shape
    print features_test.shape

    print "Train MSE: ", r_squared_train

    print "Test MSE: ", r_squared_test

    '''pca = PCA(n_components=225)
    pca.fit(features_train)
    X_train_pca = pca.transform(features_train)
    X_test_pca = pca.transform(features_test)
    print X_train_pca.shape
    print X_test_pca.shape
    new_model = Ridge()
    new_model.fit(X_train_pca, response_train)
    y_pred1 = new_model.predict(X_train_pca) #train prediction

    y_pred2 = new_model.predict(X_test_pca) #test prediction


    print "Ridge Regressor"

    print "Feature Selection Method: PCA"

    r_squared_train = mean_squared_error(response_train, y_pred1)

    r_squared_test = mean_squared_error(response_test, y_pred2)

    print "Train MSE: ", r_squared_train

    print "Test MSE: ", r_squared_test'''

    test_pca(features_train, features_test, response_train, response_test)

    # call them in here

    pass


if __name__ == "__main__":

    main()
