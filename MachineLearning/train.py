import numpy as np
from sklearn.linear_model import Ridge
import mysql.connector
import datetime as dt
import models
import datetime


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

    now = datetime.datetime.now()
    day = now.day
    year = now.year
    month = now.month

    cnx = mysql.connector.connect(
        user="wsa@wsabasketball",
        host='wsabasketball.mysql.database.azure.com',
        database="basketball",
        password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

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

    ridge = Ridge(100)
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

    ridge = Ridge(100)
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
    testXL = np.asarray(allPlayerFeatures)

    print "Number of training examples: " + str(np.shape(testXL)[0])

    # add bias term
    ones = np.ones((np.shape(testXL)[0], 1), dtype=float)
    testXL = np.hstack((ones, testXL))

    ridge = Ridge(100)
    ridge.fit(testXL, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Le" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)
