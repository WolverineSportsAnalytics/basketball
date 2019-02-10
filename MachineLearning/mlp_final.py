from algorithmClass import Algorithm

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

class MLPRegressor(Algorithm):
  

    def split_features(self, chosenFeatures):

    #first, remove the draft_kings points (not needed)
    draft_kings = [features.pop(-1) for features in self.features]

    

    #extract and remove the fanduel points (response variable)

    fanduel = [features.pop(-1) for features in self.features]

    
    for i in range(5):
        temp = [features.pop(0) for features in self.features]
        
    self.features = scale(self.features)



    #return only the chosen features from features table, and the fanduel points

    return self.features[:, chosenFeatures], fanduel

    def run_pca(X_train, X_test):
    '''applies Principal Component Analysis on data with 201 components, returns dimension-reduced training set'''
   
        
        pca = PCA(n_components=201)
        pca.fit(X_train)
        X_train_pca = pca.transform(X_train)
        X_test_pca = pca.transform(X_test)

        return X_train_pca, X_test_pca  


    def predict(self):
        self.model = Ridge(100) # set model
        self.model.fit(self.features, self.target) # fit model
        self.predictions = self.model.predict(self.features) # predict for features
        return self.predictions

    def mse(self):
        return mean_squared_error(self.target, self.predictions)


def test():
    ''' This tests and shows how predictions occur using the ridge regression object '''
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    getAllData = "select * from futures where fanduelPts is not null"
    cursor.execute(getAllData)

    features = [list(feature) for feature in cursor.fetchall()]


    # How you would import and us ridge regression 
    ridge = ridgeRegression(features)
    predictions = ridge.predict()
    print ridge.mse()

if __name__=="__main__":
    test()
