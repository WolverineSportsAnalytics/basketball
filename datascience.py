import numpy as np
from sklearn.linear_model import Ridge
import mysql.connector
import datetime as dt
import constants
import models
from sklearn.model_selection import cross_val_score
import operator

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

    alphaScore = {}

    for i in range(0,100):
        a = (float(i)/float(10))
        ridge = Ridge(alpha=a, fit_intercept=True, normalize=True)
        scores = cross_val_score(ridge, testXB, testY, cv=10)
        alphaScore[a] = scores.mean()
        print "Alpha " + str(a) + " Score: " + str(scores.mean())

    maxAlpha = max(alphaScore.iteritems(), key=operator.itemgetter(1))[0]
    print "Max Alpha: " + str(maxAlpha)
    print "Max Accuracy: " + str(alphaScore[maxAlpha])

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXB, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Ben" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    print "Training Lonzo Ball Model..."

    allPlayerFeatures = []

    cursor.execute(getFeaturesL)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    numFeatures = len(allPlayerFeatures[0])
    testXL = np.asarray(allPlayerFeatures)

    print "Number of training examples: " + str(np.shape(testXL)[0])

    # add bias term
    ones = np.ones((np.shape(testXL)[0], 1), dtype=float)
    testXL = np.hstack((ones, testXL))

    alphaScoreL = {}

    for i in range(0,100):
        a = (float(i)/float(10))
        ridge = Ridge(alpha=a, fit_intercept=True, normalize=True)
        scores = cross_val_score(ridge, testXL, testY, cv=10)
        alphaScoreL[a] = scores.mean()
        print "Alpha " + str(a) + " Score: " + str(scores.mean())

    maxAlpha = max(alphaScoreL.iteritems(), key=operator.itemgetter(1))[0]
    print "Max Alpha: " + str(maxAlpha)
    print "Max Accuracy: " + str(alphaScoreL[maxAlpha])

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXL, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Lonzo" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    print "Training Le LeBron Model..."

    allPlayerFeatures = []

    cursor.execute(getFeaturesLe)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    numFeatures = len(allPlayerFeatures[0])
    testXLe = np.asarray(allPlayerFeatures)

    print "Number of training examples: " + str(np.shape(testXL)[0])

    # add bias term
    ones = np.ones((np.shape(testXL)[0], 1), dtype=float)
    testXL = np.hstack((ones, testXL))

    alphaScoreLe = {}

    for i in range(0,100):
        a = (float(i)/float(10))
        ridge = Ridge(alpha=a, fit_intercept=True, normalize=True)
        scores = cross_val_score(ridge, testXL, testY, cv=10)
        alphaScoreLe[a] = scores.mean()
        print "Alpha " + str(a) + " Score: " + str(scores.mean())

    maxAlpha = max(alphaScoreLe.iteritems(), key=operator.itemgetter(1))[0]
    print "Max Alpha: " + str(maxAlpha)
    print "Max Accuracy: " + str(alphaScoreLe[maxAlpha])

    ridge = Ridge(alpha=maxAlpha, fit_intercept=True, normalize=True)
    ridge.fit(testXLe, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Le" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)