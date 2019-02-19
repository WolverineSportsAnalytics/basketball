from algorithmClass import Algorithm
import sklearn
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import scale
import numpy as np
from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score, mean_absolute_error
import mysql.connector
import pandas as pd
import models
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
import pickle


class MLPRegressor(Algorithm):
    def split_data(self):
        return

    def split_features(self):
        self.features = self.data
        # first, remove the draft_kings points (not needed)
        draft_kings = [features.pop(-1) for features in self.features]

        # extract and remove the fanduel points (response variable)
        self.target = [features.pop(-1) for features in self.features]

        for i in range(5):
            temp = [features.pop(0) for features in self.features]

        self.features = scale(self.features)

    def run_pca(self):
        '''applies Principal Component Analysis on data with 201 components, returns dimension-reduced training set'''

        filename = 'PCA_model.sav'
        pca = pickle.load(open(filename, 'rb'))
        pca.fit(self.features)
        self.features = pca.transform(self.features)
        print(len(self.features[0]))

    def predict(self):
        self.split_features()
        # self.run_pca()
        filename = 'MLP_model.sav'
        self.model = pickle.load(open(filename, 'rb'))
        self.predictions = self.model.predict(
            self.features)  # predict for features
        return self.predictions

    def mse(self):
        return mean_squared_error(self.target, self.predictions)

    def compare(self):
        for i in range(len(self.predictions)):
            print self.predictions[i], self.target[i]


def test():
    ''' This tests and shows how predictions occur using the ridge regression object '''
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    getAllData = "select * from futures where fanduelPts is not null and dateID = 899;"
    cursor.execute(getAllData)

    features = [list(feature) for feature in cursor.fetchall()]
    print len(features)
    print(len(features[0]))

    # How you would import and us ridge regression
    mlp = MLPRegressor(features)
    predictions = mlp.predict()
    mlp.compare()
    print predictions
    print mlp.mse()


if __name__ == "__main__":
    test()
