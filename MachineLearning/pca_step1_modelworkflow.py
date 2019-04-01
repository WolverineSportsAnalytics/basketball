from sklearn.preprocessing import scale


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

    for i in range(5):
        temp = [features.pop(0) for features in featuresMatrix]

    featuresMatrix = scale(featuresMatrix)

    # return only the chosen features from features table, and the fanduel
    # points
    return featuresMatrix[:, chosenFeatures], fanduel


def run_pca(X_train, X_test):
    '''applies Principal Component Analysis on data with 201 components, returns dimension-reduced training set'''

    #pca = PCA(n_components=201)
    # pca.fit(X_train)
    #filename = 'PCA_model.sav'
    #pickle.dump(pca, open(filename, 'wb'))
    #X_train_pca = pca.transform(X_train)
    #X_test_pca = pca.transform(X_test)
    X_train_pca = X_train
    X_test_pca = X_test

    return X_train_pca, X_test_pca
