import mysql.connector
import sklearn
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import StratifiedKFold 
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import scale
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import RandomForestRegressor
import random
import numpy as np
from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score
from sklearn.model_selection import KFold
from sklearn.feature_selection import SelectFromModel
from sklearn.svm import LinearSVC
from feature_selector import FeatureSelector
import pandas as pd

from sklearn.preprocessing import normalize

from genetic_selection import GeneticSelectionCV

def get_features_matrix(cnx, cursor, start_date, end_date):
    '''
    Will connect to database and get all the features for all players in between 
    start_date and end_date, which are date id's
    Returns matrix of all players, their features, and final performance (fanduel points scored)
    '''
    select = "Select * from futures where dateID > %s and dateID < %s and fanduelPts>10"
    days = (start_date, end_date)
    cursor.execute(select,days)
    features_tuples = cursor.fetchall()
    return [list(feature) for feature in features_tuples]

def feature_selection(train_data, fanduel_points):

    '''

    Feature selection method developed here: https://towardsdatascience.com/a-feature-selection-tool-for-machine-learning-in-python-b64dd23710f0

    

    Based off of GBM, eliminates variables with too many missing values, collinearity, zero-importance, low-cumulative importance and zero variance

    '''
    print "Data", train_data[1:,1:];
    print "Index", train_data[1:,0];
    print "Columns", train_data[0,1:];
    
    fs = FeatureSelector(data = pd.DataFrame(data=train_data[1:,1:], index=train_data[1:,0], columns=train_data[0,1:]), labels = fanduel_points);

    fs.identify_all(selection_params = {'missing_threshold': 0.6,    

                                        'correlation_threshold': 0.98, 

                                        'task': 'regression',    

                                        'eval_metric': 'auc', 

                                        'cumulative_importance': 0.99})

    return(fs.remove(methods = 'all'))

def cross_validation(clf, train_x, train_y, k):
    '''
    Takes in a model with set hyperperameters and train_x and train_y
    Will run k fold cross validation and return perfomance metrics (r2)
    can take in any model
    '''
    k_fold = KFold(5, shuffle = True)
    scores = cross_val_score(clf, train_x, train_y, cv=k_fold, n_jobs=1, scoring='neg_mean_squared_error')
    return scores


def split_features(featuresMatrix, chosenFeatures):
    '''
    Takes a matrix of features and a list of indices (chosen features) 
    to take all the features from the futures table and slim them to 
    only the features we want to train on and evaluate

    returns new featuresMatrix with only the chosenFeatures
    '''

    #first, remove the draft_kings points (not needed)
    draft_kings = [features.pop(-1) for features in featuresMatrix]
    
    #extract and remove the fanduel points (response variable)
    fanduel = [features.pop(-1) for features in featuresMatrix]
    
    featuresMatrix = scale(featuresMatrix)

    #return only the chosen features from features table, and the fanduel points
    return featuresMatrix[:, chosenFeatures], fanduel


    

def main():
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="Federer123!")
    cursor = cnx.cursor(buffered=True)

    features = get_features_matrix(cnx, cursor, 0, 900)

    
    print len(features[0])
    X_train, Y_train = split_features(features, np.linspace(0, 455, dtype=int, num=455)); #456 relevant features after removal of fanduel and draftkings
    print len(features[0])
    #X_train = normalize(X_train)
    
    estimator = LinearRegression()
    
    length = (len(X_train[1])/2, 50, 20, 10)
    print "Length", len(X_train[0])
    X = X_train[:13000]
    print "Length", len(X[0])
    Y = Y_train[:13000]
    x_test = X_train[13000:]
    y_test = Y_train[13000:]
    print y_test[0]

    hidden_layer = (length)
    #model = MLPRegressor(hidden_layer_sizes=(hidden_layer), alpha=100, activation='relu', learning_rate="adaptive")
    #model - Ridge(100)

    #Run Random Forest without Feature Selection to get Variable Importance
    '''model = linear_model.Lasso(alpha=0.01)
    model = SelectFromModel(model, prefit=True)'''

    model = RandomForestRegressor() 
    model.fit(X,Y)
    #print model.feature_importances_
    y_pred1 = model.predict(X) #train prediction
    y_pred2 = model.predict(x_test) #test prediction
    #print "MLP RELU", hidden_layer
    print "Random Forest Regressor"
    print "Feature Selection Method: None"

    
    r_squared_train = mean_squared_error(Y, y_pred1)
    r_squared_test = mean_squared_error(y_test, y_pred2)
    

    print "Train MSE: ", r_squared_train   
    print "Test MSE: ", r_squared_test

    print "Length", len(X_train[0])
    X_train = feature_selection(X,Y);
    X = X_train[:13000]
    Y= y_train[:13000]
    x_test = X_train[13000:]
    y_test = Y_train[13000:]
    

 

    '''final =[]
    count=1;
    #perform feature selection based on Random Forest's variable importance ranking
    #print model.feature_importances_
    for imp in model.feature_importances_:
        if (imp>0.002): #somewhat arbitrary criterion; could be 0.01 or 0.0001
            final.append(count)
        count+=1;
    #print count 
        
    #split features
    features = get_features_matrix(cnx, cursor, 0, 900)
    print len(features[0])
    X_train, Y_train = split_features(features, final)
    print len(X_train[0])
    length = (len(X_train[1])/2, 50, 20, 10)
    X = X_train[:13000]
    Y = Y_train[:13000]
    x_test = X_train[13000:]
    y_test = Y_train[13000:]
    print y_test[0] '''

    

    #now run Ridge regression with only the most important features
    hidden_layer = (length)
    #model = MLPRegressor(hidden_layer_sizes=(hidden_layer), alpha=100, activation='relu', learning_rate="adaptive")
    #model = Ridge(100)

    '''model.fit(X,Y)
    model_new = SelectFromModel(model, prefit=True);
    model_new = model_new.transform(X);
    
    y_pred1 = model_new.predict(X) #train prediction
    y_pred2 = model_new.predict(x_test) #test prediction '''

    model.fit(X,Y)
    y_pred1 = model.predict(X) #train prediction
    y_pred2 = model.predict(x_test) #test prediction 

    
    r_squared_train = mean_squared_error(Y, y_pred1)
    r_squared_test = mean_squared_error(y_test, y_pred2)
    k_after = count; #number of features after feature selection
                                        
    #print "MLP RELU", hidden_layer
    print "Ridge Regressor"
    print "Feature Selection Method: RF Feature Importance"
    print "Train MSE: ", r_squared_train   
    print "Test MSE: ", r_squared_test


    #perform cross-val using MSE as metric
    scores = cross_validation(model, X_train, Y_train, 5)
    print scores
    
        
    # call them in here
    pass
if __name__=="__main__":
    main()
