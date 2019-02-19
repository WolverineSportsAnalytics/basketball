def get_features_matrix(cnx, cursor, start_date, end_date):
    '''
    Will connect to database and get all the features for all players in between
    start_date and end_date, which are date id's
    Returns matrix of all players there features and final performance
    '''


def cross_validation(model, train_x, train_y, k):
    '''
    Takes in a model with set hyperperameters and train_x and train_y
    Will run k fold cross validation and return perfomance metrics (r2)
    can take in any model
    '''


def split_features(featuresMatrix, chosenFeatures):
    '''
    Takes a matrix of features and a list of indices (chosen features)
    to take all the features from the futures table and slim them to
    only the features we want to train on and evaluate

    returns new featuresMatrix with only the chosenFeatures
    '''


def main():
    # call them in here
    pass
