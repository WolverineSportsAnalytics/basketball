from algorithmClass import Algorithm
from sklearn.linear_model import Ridge
import mysql.connector
from sklearn.metrics import mean_squared_error

class ridgeRegression(Algorithm):
    def split_data(self):
        ''' This will split the data and allow you to do feature selection here '''
        self.features = self.data
        draft_kings = [features.pop(-1) for features in self.features]
        fanduel = [features.pop(-1) for features in self.features]
        self.target = fanduel

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
