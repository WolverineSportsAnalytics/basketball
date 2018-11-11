import mysql.connector
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import StratifiedKFold 
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import scale
import random
from sklearn.metrics import mean_squared_error, make_scorer

from genetic_selection import GeneticSelectionCV

def get_features_matrix(cnx, cursor, start_date, end_date):
    '''
    Will connect to database and get all the features for all players in between 
    start_date and end_date, which are date id's
    Returns matrix of all players there features and final performance
    '''
    select = "Select * from futures where dateID > %s and dateID < %s and fanduelPts>10"
    days = (start_date, end_date)
    cursor.execute(select,days)
    features_tuples = cursor.fetchall()
    return [list(feature) for feature in features_tuples]

def cross_validation(clf, train_x, train_y, k):
    '''
    Takes in a model with set hyperperameters and train_x and train_y
    Will run k fold cross validation and return perfomance metrics (r2)
    can take in any model
    '''
    k_fold = KFold(len(train_y), n_folds=k, shuffle=True, random_state=0)
    scores = cross_val_score(clf, train_x, train_y, cv=k_fold, n_jobs=1)
    return scores


def split_features(featuresMatrix, chosenFeatures):
    '''
    Takes a matrix of features and a list of indices (chosen features) 
    to take all the features from the futures table and slim them to 
    only the features we want to train on and evaluate

    returns new featuresMatrix with only the chosenFeatures
    '''
    draft_kings = [features.pop(-1) for features in featuresMatrix]
    fanduel = [features.pop(-1) for features in featuresMatrix]

    featuresMatrix = scale(featuresMatrix)
    return featuresMatrix, fanduel

def main():
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    features = get_features_matrix(cnx, cursor, 0, 900)
    
    X_train, Y_train = split_features(features, features)
    '''
    estimator = LinearRegression()
    selector = GeneticSelectionCV(estimator,
                                  cv=5,
                                  verbose=1,
                                  scoring="r2",
                                  n_population=50,
                                  crossover_proba=0.5,
                                  mutation_proba=0.2,
                                  n_generations=3,
                                  crossover_independent_proba=0.5,
                                  mutation_independent_proba=0.05,
                                  tournament_size=3,
                                  caching=True,
                                  n_jobs=-1)
    selector = selector.fit(X_train, Y_train)

    print(selector.support_)
    print len(X_train)
    exit(1)
    length = (len(X_train[1])/2)
    print length
    hidden_layer = (length)
    for i in range(1):
        print "start"
        #model = LinearRegression()
        scorer = make_scorer(mean_squared_error, greater_is_better=True)
        model = Ridge(100)
        # model = MLPRegressor(hidden_layer_sizes=(hidden_layer))
        #print hidden_layer
        #model = SVR(max_iter=10000)
        print i+1, cross_val_score(model, X_train, Y_train, cv=5, scoring=scorer)
    
    '''
    length = (len(X_train[1])/2, 50, 20, 10)
    X = X_train[:1300]
    Y = Y_train[:1300]
    x_test = X_train[1300:]
    y_test = Y_train[1300:]

    hidden_layer = (length)
    #model = MLPRegressor(hidden_layer_sizes=(hidden_layer), alpha=100, activation='relu', learning_rate="adaptive")
    model = Ridge()
    model.fit(X,Y)
    y_pred1 = model.predict(X)
    #print "MLP RELU", hidden_layer
    print "Ridge Regression ( no reg):"
    print "Train MSE:", mean_squared_error(Y, y_pred1)
    y_pred2 = model.predict(x_test)
    print "Test MSE:", mean_squared_error(y_test, y_pred2)
    

    # call them in here
    pass
if __name__=="__main__":
    main()
