import numpy as np
import mysql.connector
import datetime as dt
import models
import datetime
from ridge_final import RidgeRegressor
from mlp_final import MLPRegressor
from datetime import date as wsadate
from datetime import timedelta
import os

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def makeProjections(day, month, year, cursor, cnx):
    # dates to retrieve data for batter test data
    # start date

    dir_path = os.getcwd()

    if dir_path.split("/")[-1] == "basketball":
        os.chdir("MachineLearning")

    dateID = getDate(day, month, year, cursor)
    print dateID

    print "Projecting with Ben Simmons Model..."

    benSimmonsModel = models.benSimmonsModel

    lonzoBallModel = models.lonzoBallModel

    leModel = models.leModel

    getFeaturesB = "SELECT "

    for m in (benSimmonsModel):
        getFeaturesB += m
        getFeaturesB += ", "
    getFeaturesB = getFeaturesB[:-2]
    getFeaturesB += " FROM futures"  # turn into numpy arrays
    getFeaturesB += " WHERE dateID = "
    getFeaturesB += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesB)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    targetX = np.asarray(allPlayerFeatures)

    print "Number of target examples: " + str(np.shape(targetX)[0])

    # add bias term
    ones = np.ones((np.shape(targetX)[0], 1), dtype=float)
    targetX = np.hstack((ones, targetX))

    outfile = open("coefBen.npz", 'r')
    thetaSKLearnRidge = np.load(outfile)
    # predict
    targetBenSimmons = targetX.dot(np.transpose(thetaSKLearnRidge))

    getFeaturesL = "SELECT "

    for m in (lonzoBallModel):
        getFeaturesL += m
        getFeaturesL += ", "
    getFeaturesL = getFeaturesL[:-2]
    getFeaturesL += " FROM futures"  # turn into numpy arrays
    getFeaturesL += " WHERE dateID = "
    getFeaturesL += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesL)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    targetX = np.asarray(allPlayerFeatures)

    print "Projecting with Lonzo Ball Model..."

    print "Number of target examples: " + str(np.shape(targetX)[0])

    # add bias term
    ones = np.ones((np.shape(targetX)[0], 1), dtype=float)
    targetX = np.hstack((ones, targetX))

    outfile = open("coefLonzo.npz", 'r')
    thetaSKLearnRidge = np.load(outfile)

    targetLonzoBall = targetX.dot(np.transpose(thetaSKLearnRidge))
    # predict

    print "Predicting Le Lebron Model"

    getFeaturesLe = "SELECT "

    for m in (leModel):
        getFeaturesLe += m
        getFeaturesLe += ", "
    getFeaturesLe = getFeaturesLe[:-2]
    getFeaturesLe += " FROM futures"  # turn into numpy arrays
    getFeaturesLe += " WHERE dateID = "
    getFeaturesLe += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesLe)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    targetX = np.asarray(allPlayerFeatures)

    print "Projecting with Le Lebron Ball Model..."

    print "Number of target examples: " + str(np.shape(targetX)[0])

    # add bias term
    ones = np.ones((np.shape(targetX)[0], 1), dtype=float)
    targetX = np.hstack((ones, targetX))

    outfile = open("coefLe.npz", 'r')
    thetaSKLearnRidge = np.load(outfile)

    targetLeModel = targetX.dot(np.transpose(thetaSKLearnRidge))

    # Pick Ridge Regressions
    print "Predicting with Ridge Regression"

    getAllData = "select * from futures where dateID=" + str(dateID)
    cursor.execute(getAllData)
    features = [list(feature) for feature in cursor.fetchall()]  # get the features

    ridge = RidgeRegressor(features)
    ridgePredictions = ridge.predict()

    # picking MLP Regressions
    print "Predicting with MLP Regression"
    getAllData = "select * from futures where dateID=" + str(dateID)
    cursor.execute(getAllData)
    features2 = [list(feature) for feature in cursor.fetchall()]  # get the features

    mlp = MLPRegressor(features2)
    mlpPredictions = mlp.predict()

    statement = "SELECT playerID"
    statement += " FROM futures"  # turn into numpy arrays
    statement += " WHERE dateID = "
    statement += str(dateID)

    cursor.execute(statement)

    playerIDs = cursor.fetchall()

    for counter, x in enumerate(playerIDs):
        playerID = playerIDs[counter]
        hardawayProj = 0
        mlpProj = float(mlpPredictions[counter])
        ridgeProj = float(ridgePredictions[counter])
        leProj = float(targetLeModel[counter])
        simmonsProj = float(targetBenSimmons[counter])
        zoProj = float(targetLonzoBall[counter])

        updateBattersDKPoints = "UPDATE performance SET simmonsProj = %s, zoProj = %s, hardawayProj = %s, leProj = %s, ridgeProj = %s, mlpProj = %s WHERE dateID = %s AND playerID = %s"
        updateBatterDKPointsData = (
            simmonsProj, zoProj, hardawayProj, leProj, ridgeProj, mlpProj,
            dateID, x[0])
        print updateBatterDKPointsData
        cursor.execute(updateBattersDKPoints, updateBatterDKPointsData)
        cnx.commit()

    print "Predicted FD Points for Players"

    os.chdir(dir_path)


def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP


if __name__ == "__main__":
    print "Loading data..."

    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    startYear = 2016
    startMonth = 11
    startDay = 13

    endYear = 2018
    endMonth = 4
    endDay = 25


    start_date = wsadate(startYear, startMonth, startDay)
    end_date = wsadate(endYear, endMonth, endDay)

    for single_date in daterange(start_date, end_date):
        try:

            makeProjections(single_date.day, single_date.month, single_date.year, cursor, cnx)
        except:
            print single_date
    