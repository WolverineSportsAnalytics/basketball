import mysql.connector
import pca_step1_modelworkflow
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Ridge
import sklearn
from sklearn.preprocessing import scale
import numpy as np
from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score, mean_absolute_error
import pandas as pd
import models
import pickle
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize


def train_model():
    '''trains an MLP Regressor model on PCA-reduced data and tunes the hyperparameters. Returns the model'''
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="Federer123!")
    cursor = cnx.cursor(buffered=True)

    # extract features from database
    features = pca_step1_modelworkflow.get_features_matrix(cnx, cursor, 0, 900)

    # get features and response variable
    features, response = pca_step1_modelworkflow.split_features(features, np.linspace(
        0, 450, dtype=int, num=451))  # 456 relevant features after removal of fanduel and draftkings

    # run pca to get sparse representation of data
    features_train = features[:14000]
    response_train = response[:14000]
    features_test = features[14000:]
    response_test = response[14000:]
    features_train_pca, features_test_pca = pca_step1_modelworkflow.run_pca(
        features_train, features_test)

    # Run Ridge without Feature Selection to get Variable Importance
    learning_rate_init = [0.00001 * 10**i for i in range(5)]
    shuffle = [True, False]
    momentum = [0.2 + 0.2 * i for i in range(4)]
    nesterovs_momentum = [True, False]
    early_stopping = [True, False]
    hyperparams = dict(momentum=momentum)

    #hyperparams = dict(learning_rate_init = learning_rate_init, shuffle = shuffle, momentum = momentum, nesterovs_momentum = nesterovs_momentum, early_stopping = early_stopping);
    #grid = GridSearchCV(estimator = MLPRegressor(alpha = 100.0, activation = 'relu', learning_rate = 'adaptive', solver = 'sgd', max_iter = 600), param_grid = hyperparams, scoring = 'neg_mean_squared_error')
    #grid_result = grid.fit(features_train_pca, response_train)
    # print grid_result.best_params_
    mses = []

    model = Ridge(100)
    model.fit(features_train_pca, response_train)

    filename = 'Ridge100_model.sav'
    pickle.dump(model, open(filename, 'wb'))

    y_pred1 = model.predict(features_test_pca)  # test prediction
    mses.append(mean_squared_error(y_pred1, response_test))

    print mses


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


def main():
    train_model()


if __name__ == "__main__":

    main()
