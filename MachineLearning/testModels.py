import mysql.connector
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import StratifiedKFold 
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import scale
from sklearn.ensemble import ExtraTreesRegressor
import random
import numpy as np
from sklearn.metrics import mean_squared_error, make_scorer, explained_variance_score
from sklearn.model_selection import KFold

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

def cross_validation(clf, train_x, train_y, k):
    '''
    Takes in a model with set hyperperameters and train_x and train_y
    Will run k fold cross validation and return perfomance metrics (r2)
    can take in any model
    '''
    k_fold = KFold(5, shuffle = True)
    scores = cross_val_score(clf, train_x, train_y, cv=k_fold, n_jobs=1, scoring='explained_variance')
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

    
    
    X_train, Y_train = split_features(features, np.linspace(0, 455, dtype=int)); #456 relevant features after removal of fanduel and draftkings
    #X_train = normalize(X_train)
    
    estimator = LinearRegression()
    '''selector = GeneticSelectionCV(estimator,
                                  cv=5,
                                  verbose=1,
                                  scoring="r2",
                                  n_population=50,
                                  crossover_proba=0.5,
                                  mutation_proba=0.2,
                                  n_generations=1,
                                  crossover_independent_proba=0.5,
                                  mutation_independent_proba=0.05,
                                  tournament_size=3,
                                  caching=True,
                                  n_jobs=-1)
    selector = selector.fit(X_train, Y_train)

    #print(selector.support_)
    selection = selector.support_
    final= []
    index = 0;
    #perform feature selection
    for item in selection:
        if(item =='True'):
            final.append(index)
        index+=1;
    #Extract selected features
    X_train, Y_train = split_features(features, final)
    '''
    '''
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
    #model - Ridge(100)

    #Run Random Forest without Feature Selection to get Variable Importance
    model = ExtraTreesRegressor() 
    model.fit(X,Y)
    y_pred1 = model.predict(X) #train prediction
    y_pred2 = model.predict(x_test) #test prediction
    #print "MLP RELU", hidden_layer
    print "Random Forest Regressor"
    print "Feature Selection Method: None"

    
    r_squared_train = explained_variance_score(Y, y_pred1)
    r_squared_test = explained_variance_score(y_test, y_pred2)
    
    
    n_train = len(X); # number of train samples
    n_test = len(x_test); #number of test samples
    k_before = 455; #number of features prior to feature selection
    

    print "Train Adjusted r squared:", 1-((1-r_squared_train)*(n_train-1)/(n_train-k_before-1))
    
    print "Test adjusted r squared:", 1-((1-r_squared_test)*(n_test-1)/(n_test-k_before-1))

 

    final =[]
    count=1;
    #perform feature selection based on Random Forest's variable importance ranking
    print model.feature_importances_
    for imp in model.feature_importances_:
        if (imp>0.001): #somewhat arbitrary criterion; could be 0.01 or 0.0001
            final.append(count)
        count+=1;
        
    #split features
    X_train, Y_train = split_features(features, final)
    length = (len(X_train[1])/2, 50, 20, 10)
    X = X_train[:1300]
    Y = Y_train[:1300]
    x_test = X_train[1300:]
    y_test = Y_train[1300:]

    #now run Ridge regression with only the most important features
    hidden_layer = (length)
    #model = MLPRegressor(hidden_layer_sizes=(hidden_layer), alpha=100, activation='relu', learning_rate="adaptive")
    model = Ridge(100)
    #model = ExtraTreesRegressor()
    model.fit(X,Y)
    y_pred1 = model.predict(X) #train prediction
    y_pred2 = model.predict(x_test) #test prediction

    
    r_squared_train = explained_variance_score(Y, y_pred1)
    r_squared_test = explained_variance_score(y_test, y_pred2)
    k_after = count; #number of features after feature selection
                                        
    #print "MLP RELU", hidden_layer
    print "Ridge Regressor"
    print "Feature Selection Method: RF Feature Importance"
    print "Train adjusted R squared:", 1-((1-r_squared_train)*(n_train-1)/(n_train-k_after-1))
   
    print "Test adjusted R squared: ", 1-((1-r_squared_test)*(n_test-1)/(n_test-k_after-1))


    #perform cross-val using r^2 as metric
    scores = cross_validation(model, X_train, Y_train, 5)
    print scores
    
        
        

    # call them in here
    pass
if __name__=="__main__":
    main()
