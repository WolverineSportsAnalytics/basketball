import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, RidgeCV
import mysql.connector
import datetime as dt
import constants
import models

def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP

if __name__ == "__main__":

    # dates to retrieve data for batter test data
    # start date
    year = constants.yearP
    month = constants.monthP
    day = constants.dayP

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    dateID = getDate(day, month, year, cursor)

    print "Training Ben Simmons Model..."


    benSimmonsModel = models.benSimmonsModel

    lonzoBallModel = models.lonzoBallModel

    leModel = models.leModel

    getFeaturesB = "SELECT "

    for m in (benSimmonsModel):
        getFeaturesB += m
        getFeaturesB += ", "
    getFeaturesB = getFeaturesB[:-2]
    getFeaturesB += " FROM futures"    # turn into numpy arrays
    getFeaturesB += " WHERE dateID < "
    getFeaturesB += str(dateID)

    getFeaturesL = "SELECT "

    for m in (lonzoBallModel):
        getFeaturesL += m
        getFeaturesL += ", "
    getFeaturesL = getFeaturesL[:-2]
    getFeaturesL += " FROM futures"  # turn into numpy arrays
    getFeaturesL += " WHERE dateID < "
    getFeaturesL += str(dateID)

    getFeaturesLe = "SELECT "

    for m in (leModel):
        getFeaturesLe += m
        getFeaturesLe += ", "
    getFeaturesLe = getFeaturesLe[:-2]
    getFeaturesLe += " FROM futures"  # turn into numpy arrays
    getFeaturesLe += " WHERE dateID < "
    getFeaturesLe += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesB)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    FDTargets = []

    getTargets = "SELECT fanduelPts FROM futures WHERE dateID < %s"
    getTargetsData = (dateID,)
    cursor.execute(getTargets, getTargetsData)
    targets = cursor.fetchall()

    for tar in targets:
        FDTargets.append(tar)

    numFeatures = len(allPlayerFeatures[0])
    testXB = np.asarray(allPlayerFeatures)
    testY = np.asarray(FDTargets)

    print "Number of training examples: " + str(np.shape(testXB)[0])

    # add bias term
    ones = np.ones((np.shape(testXB)[0], 1), dtype=float)
    testXB = np.hstack((ones, testXB))

    alphas = (2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8)

    ridgecv = RidgeCV(alphas=alphas, scoring='neg_mean_squared_error', normalize=False, cv=10, fit_intercept=True)
    ridgecv.fit(testXB, testY)
    print "Optimal Alpha = " + str(ridgecv.alpha_)
    maxAlpha = ridgecv.alpha_

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXB, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Ben" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    benSimmonsModel = ['intercept'] + benSimmonsModel
    simPandas = np.array(benSimmonsModel).ravel()
    print(pd.Series((ridge.coef_).ravel(), index=simPandas))  # Print coefficients



    print "Training Lonzo Ball Model..."

    allPlayerFeatures = []

    cursor.execute(getFeaturesL)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    numFeatures = len(allPlayerFeatures[0])
    testXL = np.asarray(allPlayerFeatures)

    # get fd targets
    FDTargets = []

    getTargets = "SELECT fanduelPts FROM futures WHERE dateID < %s"
    getTargetsData = (dateID,)
    cursor.execute(getTargets, getTargetsData)
    targets = cursor.fetchall()

    for tar in targets:
        FDTargets.append(tar)

    testY = np.asarray(FDTargets)

    print "Number of training examples: " + str(np.shape(testXL)[0])

    # add bias term
    ones = np.ones((np.shape(testXL)[0], 1), dtype=float)
    testXL = np.hstack((ones, testXL))

    alphas = (10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9)

    ridgecv = RidgeCV(alphas=alphas, scoring='neg_mean_squared_error', normalize=False, cv=10, fit_intercept=True)
    ridgecv.fit(testXL, testY)
    print "Optimal Alpha = " + str(ridgecv.alpha_)
    maxAlpha = ridgecv.alpha_

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXL, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Lonzo" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    lonzoBallModel = ['intercept'] + lonzoBallModel
    simPandas = np.array(lonzoBallModel).ravel()
    print(pd.Series((ridge.coef_).ravel(), index=simPandas))  # Print coefficients




    print "Training Le LeBron Model..."

    allPlayerFeatures = []

    cursor.execute(getFeaturesLe)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    numFeatures = len(allPlayerFeatures[0])
    testXLe = np.asarray(allPlayerFeatures)

    print "Number of training examples: " + str(np.shape(testXLe)[0])

    # add bias term
    ones = np.ones((np.shape(testXLe)[0], 1), dtype=float)
    testXLe = np.hstack((ones, testXLe))

    # get fd targets
    FDTargets = []

    getTargets = "SELECT fanduelPts FROM futures WHERE dateID < %s"
    getTargetsData = (dateID,)
    cursor.execute(getTargets, getTargetsData)
    targets = cursor.fetchall()

    for tar in targets:
        FDTargets.append(tar)

    numFeatures = len(allPlayerFeatures[0])
    testY = np.asarray(FDTargets)

    alphas = (5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7)

    ridgecv = RidgeCV(alphas=alphas, scoring='neg_mean_squared_error', normalize=False, cv=10, fit_intercept=True)
    ridgecv.fit(testXLe, testY)
    print "Optimal Alpha = " + str(ridgecv.alpha_)
    maxAlpha = ridgecv.alpha_

    '''
    alphaScoreLe = {}

    for i in range(0,100):
        a = (float(i)/float(10))
        ridge = Ridge(alpha=a, fit_intercept=True, normalize=True)
        scores = cross_val_score(ridge, testXLe, testY, scoring='neg_mean_squared_error', cv=10)
        alphaScoreLe[a] = scores.mean()
        print "Alpha " + str(a) + " Score: " + str(scores.mean())

    maxAlpha = max(alphaScoreLe.iteritems(), key=operator.itemgetter(1))[0]
    print "Max Alpha: " + str(maxAlpha)
    print "Max Accuracy: " + str(alphaScoreLe[maxAlpha])
    '''

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXLe, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Le" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    leModel = ['intercept'] + leModel
    simPandas = np.array(leModel).ravel()
    print(pd.Series((ridge.coef_).ravel(), index=simPandas))  # Print coefficients