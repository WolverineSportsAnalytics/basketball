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
from scipy.stats import norm

def train_model():
    '''trains a Ridge Regressor model on PCA-reduced data and tunes the hyperparameters. Returns the model'''
    cnx = mysql.connector.connect(user="wsa",
                                  host="34.68.250.121",
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    # extract features from database
    features = pca_step1_modelworkflow.get_features_matrix(cnx, cursor, 0, 900)

    std_dev = []

    # get player ids and std dev of fanduel points for each player
    for player in features[14000:] :
        playerid = player[1]
        get_fanduel = "SELECT fanduelPts from performance WHERE fanduelPts is not null AND playerID = " + str(playerid)
        cursor.execute(get_fanduel)
        fanduel = cursor.fetchall()
        std_dev.append(np.nanstd(fanduel));

    # get features and response variable
    features, response = pca_step1_modelworkflow.split_features(features, np.linspace(
        0, 450, dtype=int, num=451))  # 456 relevant features after removal of fanduel and draftkings

    # run pca to get sparse representation of data
    features_train = features[:14000]
    response_train = response[:14000]
    features_test = features[14000:]
    response_test = response[14000:]
    
    
    features_train_pca, features_test_pca = pca_step1_modelworkflow.run_pca(features_train, features_test)
    mses = []

    model = Ridge(100)
    model.fit(features_train_pca, response_train)

    filename = 'Ridge100_model.sav'
    pickle.dump(model, open(filename, 'wb'))
        
    
    y_pred1 = model.predict(features_test_pca)# test prediction
    lowerbound = [];
    upperbound = [];
    prediction = [];
    triples = [];
    number_in_range = 0
    for i in range(len(features_test)):
        prediction.append(y_pred1[i])
        lowerbound.append(y_pred1[i] - norm.ppf(0.975)*std_dev[i])
        upperbound.append(y_pred1[i] + norm.ppf(0.975)*std_dev[i])
        triples.append([lowerbound[i], prediction[i], upperbound[i]])
        if (lowerbound[i] < response_train[i] < upperbound[i]) :
            number_in_range += 1
        else:
            # this is the case we werent in range
            print " Range {}-{} : outcome {}".format(lowerbound[i], upperbound[i], response_train[i])
        
    
    mses.append(mean_squared_error(y_pred1, response_test))

    
    print "Mean Squared Error"
    print mses
    
    print "Percent in Range"
    print float(number_in_range)/float(len(response_test))



    

def main():
    train_model()


if __name__ == "__main__":

    main()
