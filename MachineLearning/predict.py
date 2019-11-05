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

# modelList is a list of strings of model names (ex. modelList=["mlp", "ridge"])
def makeProjections(modelList, dateID, cursor, cnx):
    dir_path = os.getcwd()

    if dir_path.split("/")[-1] == "basketball":
        os.chdir("MachineLearning")

    print "DATE: " + str(dateID)

    for model in modelList:
        print "Predicting with " + model + " regression"

        getAllData = "select * from futures where dateID=" + str(dateID)
        cursor.execute(getAllData)
        features = [list(feature) for feature in cursor.fetchall()]

        regressor = None
        if model == "mlp":
            regressor = MLPRegressor(features)
        elif model == "ridge":
            regressor = RidgeRegressor(features)

        predictions = regressor.predict()

        statement = "SELECT playerID"
        statement += " FROM futures"
        statement += " WHERE dateID = "
        statement += str(dateID)

        cursor.execute(statement)

        playerIDs = cursor.fetchall()

        for counter, x in enumerate(playerIDs):
            projections = float(predictions[counter])
            updateStatement = "UPDATE performance SET " + model + "Proj = %s WHERE dateID = %s AND playerID = %s"
            updateData = (projections, dateID, x[0])
            print updateData
            cursor.execute(updateStatement, updateData)
            cnx.commit()

        print "Finished predicting FD Points for players using " + model + " model"

    os.chdir(dir_path)

# Predict using Simmons Model and update performance table
def makeSimmonsPrediction(dateID, cursor, cnx):
    dir_path = os.getcwd()

    if dir_path.split("/")[-1] == "basketball":
        os.chdir("MachineLearning")

    print "DATE: " + dateID

    print "Projecting with Ben Simmons Model..."

    benSimmonsModel = models.benSimmonsModel

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

    statement = "SELECT playerID"
    statement += " FROM futures"  # turn into numpy arrays
    statement += " WHERE dateID = "
    statement += str(dateID)

    cursor.execute(statement)

    playerIDs = cursor.fetchall()

    for counter, x in enumerate(playerIDs):
        simmonsProj = float(targetBenSimmons[counter])

        updateBattersDKPoints = "UPDATE performance SET simmonsProj = %s WHERE dateID = %s AND playerID = %s"
        updateBatterDKPointsData = (
            simmonsProj,
            dateID, x[0])
        print updateBatterDKPointsData
        cursor.execute(updateBattersDKPoints, updateBatterDKPointsData)
        cnx.commit()

    print "Predicted FD Points for Simmons Model"
    
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
            dateID = getDate(single_date.day, single_date.month, single_date.year, cursor)
            makeProjections(dateID, cursor, cnx)
        except:
            print single_date
