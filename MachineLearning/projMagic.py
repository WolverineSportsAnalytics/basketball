import numpy as np
import mysql.connector
import datetime as dt

import models
import mlp_final as mp
from ridge_final import RidgeRegressor
from datetime import date as wsadate
from datetime import timedelta

from scipy.stats import norm

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def actualProjMagic(day, month, year, cursor):
    dateID = getDate(day, month, year, cursor)

    print "Projecting with Ben Simmons Model..."


    benSimmonsModel = models.benSimmonsModel

    lonzoBallModel = models.lonzoBallModel

    leModel = models.leModel

    getFeaturesB = "SELECT "

    for m in (benSimmonsModel):
        getFeaturesB += m
        getFeaturesB += ", "
    getFeaturesB = getFeaturesB[:-2]
    getFeaturesB += " FROM futures"    # turn into numpy arrays
    getFeaturesB += " WHERE dateID = "
    getFeaturesB += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesB)

    features = cursor.fetchall()
    if len(features == 0):      #add a check to see if there were even any games played that day\
        return

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

    statement = "SELECT playerID"
    statement += " FROM futures"    # turn into numpy arrays
    statement += " WHERE dateID = "
    statement += str(dateID)

    cursor.execute(statement)

    playerIDs = cursor.fetchall()

    for counter, x in enumerate(playerIDs):
        playerID = playerIDs[counter]
        hardawayProj = 0
        leProj = float(targetLeModel[counter])
        simmonsProj = float(targetBenSimmons[counter])
        zoProj = float(targetLonzoBall[counter])

        updateBattersDKPoints = "UPDATE performance SET simmonsProj = %s, zoProj = %s, hardawayProj = %s, leProj = %s WHERE dateID = %s AND playerID = %s"
        updateBatterDKPointsData = (
            simmonsProj, zoProj, hardawayProj, leProj,
            dateID, x[0])
        cursor.execute(updateBattersDKPoints, updateBatterDKPointsData)
        cnx.commit()

    print "Predicted FD Points for Players"

def projMagicMLP(day, month, year, cursor):
    dateID = getDate(day, month, year, cursor)

    print "Projecting with MLP Model..."
    print dateID
    getAllData = "select * from futures where fanduelPts is not null and dateID = %s"
    newDateID = (dateID,)
    cursor.execute(getAllData, newDateID)

    features = [list(feature) for feature in cursor.fetchall()]
    # print features
    # print(len(features[0]))

    # How you would import and us ridge regression
    mlp = mp.MLPRegressor(features)
    predictions = mlp.predict()
    mlp.compare()
    print len(predictions)
    print mlp.mse()

    # allPlayerFeatures = []
    #
    # cursor.execute(getFeaturesB)
    #
    # features = cursor.fetchall()
    # if len(features == 0):      #add a check to see if there were even any games played that day\
    #     return
    #
    # for feat in features:
    #     allPlayerFeatures.append(feat)
    #
    # targetX = np.asarray(allPlayerFeatures)
    #
    # print "Number of target examples: " + str(np.shape(targetX)[0])
    #
    # # add bias term
    # ones = np.ones((np.shape(targetX)[0], 1), dtype=float)
    # targetX = np.hstack((ones, targetX))
    #
    # outfile = open("coefBen.npz", 'r')
    # thetaSKLearnRidge = np.load(outfile)
    # # predict
    # targetBenSimmons = targetX.dot(np.transpose(thetaSKLearnRidge))

def predictRidgeConfidence(cursor, cnx, dateID):
    getAllData = "select * from futures where dateID=" + str(dateID)
    cursor.execute(getAllData)
    features = [list(feature) for feature in cursor.fetchall()] # get the features

    std_dev = [] # stdv of all players
    player_ids = []
    for player in features:
        playerid = player[1]
        player_ids.append(playerid)
        get_fanduel = "SELECT fanduelPts from performance WHERE fanduelPts is not null AND playerID = " + str(playerid)
        cursor.execute(get_fanduel)
        fanduel = cursor.fetchall()
        std_dev.append(np.nanstd(fanduel));

    ridge = RidgeRegressor(features)
    ridgePredictions = ridge.predict()



    lowerbound = []
    upperbound = []
    prediction = []
    triples = []

    ''' This is a sanity check for all are same lenght '''
    if len(std_dev) != len(ridgePredictions) != len(features) :
        print "Warning they are not matched"
        print "STD_DEV {} Predictions {} Players {}".format(len(std_dev), len(ridgePredictions), len(player_ids))


    ''' Print that '''
    for i in range(len(ridgePredictions)):
        prediction.append(ridgePredictions[i])
        lowerbound.append(ridgePredictions[i] - norm.ppf(0.95)*std_dev[i])
        upperbound.append(ridgePredictions[i] + norm.ppf(0.95)*std_dev[i])
        triples.append([lowerbound[i], prediction[i], upperbound[i]])

    for i in range(len(ridgePredictions)):
        update_ridgeconfStatement = "UPDATE performance SET ridgeFloor = %s, ridgeProj = %s, ridgeCeil = %s WHERE dateID = %s AND playerID = %s"
        update_ridgeconfData = (
            str(triples[i][0]), str(triples[i][1]), str(triples[i][2]),
            str(dateID), str(player_ids[i]))
        cursor.execute(update_ridgeconfStatement, update_ridgeconfData)
        cnx.commit()


def predictRidge(day, month, year, cursor):
    # print "Predicting with Ridge Regression"
    dateID = getDate(day, month, year, cursor)

    getAllData = "select * from futures where dateID=" + str(dateID)
    cursor.execute(getAllData)
    features = [list(feature) for feature in cursor.fetchall()] # get the features
    print getAllData
    print features
    ridge = RidgeRegressor(features)
    ridgePredictions = ridge.predict()

    statement = "SELECT playerID"
    statement += " FROM futures"    # turn into numpy arrays
    statement += " WHERE dateID = "
    statement += str(dateID)

    cursor.execute(statement)

    playerIDs = cursor.fetchall()
    print statement
    print playerIDs

    for counter, x in enumerate(playerIDs):
        playerID = playerIDs[counter]
        ridgeProj = float(ridgePredictions[counter])

        updateBattersDKPoints = "UPDATE performance SET ridgeProj = %s WHERE dateID = %s AND playerID = %s"
        updateBatterDKPointsData = (ridgeProj, dateID, x[0])
        print updateBatterDKPointsData
        cursor.execute(updateBattersDKPoints, updateBatterDKPointsData)
        cnx.commit()

def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP

def auto(day, month, year):
    print "Loading data..."

    cnx = mysql.connector.connect(user="wsa",
                                  host="34.68.250.121",
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    actualProjMagic(day, month, year)

if __name__ == "__main__":
    print "Loading data..."

    cnx = mysql.connector.connect(user="wsa",
                                  host="34.68.250.121",
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    startYear = 2018
    startMonth = 2
    startDay = 8

    endYear = 2018
    endMonth = 2
    endDay = 9

    start_date = wsadate(startYear, startMonth, startDay)
    end_date = wsadate(endYear, endMonth, endDay)

    for single_date in daterange(start_date, end_date):
        # predictRidge(single_date.day, single_date.month, single_date.year, cursor)

        dateID = getDate(single_date.day, single_date.month, single_date.year, cursor)
        predictRidgeConfidence(cursor, cnx, dateID)
        exit(1)

    cursor.close()
    cnx.commit()
    cnx.close()
