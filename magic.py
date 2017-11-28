import numpy as np
import scipy as sp
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge, LinearRegression
import pandas as pd
import mysql.connector
import os
import datetime as dt
from itertools import chain
import constants
import warnings
from tempfile import TemporaryFile


def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP


def getDates(day, month, year, numdays, cursor):
    base = dt.date(year, month, day)
    dateList = [base - dt.timedelta(days=x) for x in range(0, numdays)]

    # get date ids from database
    gameIDs = []
    for date in dateList:
        findGame = "SELECT iddates FROM new_dates WHERE date = %s"
        findGameData = (date,)
        cursor.execute(findGame, findGameData)

        for game in cursor:
            gameIDs.append(game[0])

    return gameIDs


def mapFeatures(X):
    '''
    MAPFEATURE Feature mapping function to polynomial features
    MAPFEATURE(X1, X2) maps the two input features
    to quadratic features used in the regularization exercise.
    Returns a new feature array with more features, comprising of
    X1, X2, X1.^2, X2.^2, X1*X2, X1*X2.^2, etc..
    Inputs X1, X2 must be the same size
    :param X:
    :return: XTransform
    '''

    degree = 3

    poly = PolynomialFeatures(degree)
    XTransform = poly.fit_transform(X)

    return XTransform


def computCostMulti(X, y, theta):
    '''
    COMPUTECOSTMULTI Compute cost for linear regression with multiple variables
    J = COMPUTECOSTMULTI(X, y, theta) computes the cost of using theta as the
    parameter for linear regression to fit the data points in X and y
    '''

    # Initialize some useful values
    m = np.shape(y)[0]

    # Cost
    h = X.dot(np.transpose(theta))
    error = (h - y)
    J = ((np.transpose(error).dot(error)) / (2 * m))

    return J


def featureNormalize(X):
    '''
    FEATURENORMALIZE Normalizes the features in X FEATURENORMALIZE(X) returns a normalized version of X where
    the mean value of each feature is 0 and the standard deviation is 1. This is often a good preprocessing step
    to do when working with learning algorithms. Ignores the bias feature
    '''

    X_norm = X
    mu = np.zeros((1, np.shape(X)[1]), dtype=float)
    sigma = np.zeros((1, np.shape(X)[1]), dtype=float)

    numFeatures = np.shape(X)[1]

    i = 0
    while i < numFeatures:
        feature = X[:, i]
        mu[1, i] = np.mean(feature)
        sigma[1, i] = np.std(feature)
        feature = (feature - (mu[1, i])) / (sigma[1, i])
        X_norm[:, i] = feature

        i = i + 1

    return X_norm, mu, sigma


def gradientDescentMulti(X, y, theta, alpha, numIters):
    # Initializ some useful values
    m = np.shape(y)[0]

    # number of training examples
    thetaz = np.shape(theta)[1]

    i = 0
    costHistory = []
    iterHistory = []

    previousJ = 1000000000
    optimialIteration = False
    optimalIterNumber = 0
    while i < numIters:
        h = X.dot(np.transpose(theta))
        error = (h - y)

        j = 0
        while j < thetaz:
            xColumn = X[:, j]
            partialD = np.transpose(error).dot(xColumn)
            valueSet = ((theta[0, j]) - (alpha * partialD) / m)
            theta[0, j] = valueSet
            j = j + 1

        J = computCostMulti(X, y, theta)
        if ((previousJ - J[0, 0]) <= 0.001) and (not optimialIteration):
            optimalIterNumber = (i + 1)
            optimialIteration = True
            print "Optimal # of Iterations: " + str(optimalIterNumber)

        previousJ = J[0, 0]
        costHistory.append(J[0, 0])
        iterHistory.append(i)

        i = i + 1

    return theta, costHistory, iterHistory


if __name__ == "__main__":
    print "Loading data..."

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    # predict data
    # date to predict
    yearP = constants.yearP
    monthP = constants.monthP
    dayP = constants.dayP

    # dates to retrieve data for batter test data
    # start date
    year = constants.gdStartYear
    month = constants.gdStartMonth
    day = constants.gdStartDay

    numdays = constants.numdaysGradientDescent

    warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

    dateIDs = getDates(day, month, year, numdays, cursor)

    # week 2 lonzo ball data - feature, target - score
    # ..........
    # .......
    # week 4 day - lonzo ball's data - feature, target - ?

    numpyDataArrays = []

    # add minutes constraint
    get_players = "Select playerID from performance where dateID = %s"
    getDailyPlayerAvg = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_daily_avg WHERE dateID = %s AND playerID = %s"
    getPerformanceDataForEachPlayer = "SELECT playerID, dateID, fanduel, draftkings, fanduelPosition, draftkingsPosition, team, opponent, fanduelPts, draftkingsPts FROM performance WHERE dateID = %s AND minutesPlayed IS NOT NULL and minutesPlayed >= 10 and projMinutes IS NOT NULL"
    getTeamData = "SELECT wins, losses, ORT, DRT, avgPointsAllowed, avgPointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, offensiveReboundPercent, FT/FGA, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, points1Q, points2Q, points3Q, points4Q FROM team_daily_avg_performance WHERE dateID = %s AND dailyTeamID = %s"

    get_ball_handlers = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_ball_handlers WHERE dateID = %s and dailyTeamID = %s"
    get_wings = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_wings where dateID = %s and dailyTeamID = %s"
    get_bigs = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_bigs WHERE dateID = %s and dailyTeamID = %s"
    get_centers = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_centers WHERE dateID = %s and dailyTeamID = %s"

    # execute command + load into numpy array
    playersPlaying = []
    for date in dateIDs:
        dateD = (date,)
        cursor.execute(getPerformanceDataForEachPlayer, dateD)

        results = cursor.fetchall()
        for player in results:
            playersPlaying.append(player)

    # get daily_player_avg
    # get opp_team stats
    # get self_team stats
    # get opp_vs_player position states
    # from perfromance get fanduel point for taraget
    team_ref_query = "SELECT teamID FROM team_reference WHERE bbreff = %s"

    counter = 0

    allPlayerFeatures = []
    print len(playersPlaying)
    for player in playersPlaying:
        indvPlayerData = []
        indvPlayerData.append(player[2])
        indvPlayerData.append(player[3])
        basicQueryData = (player[1], player[0])
        cursor.execute(getDailyPlayerAvg, basicQueryData)

        playerDailyAvgResult = cursor.fetchall()

        # append playerDailyAvgResult to indvPlayerData
        for item in playerDailyAvgResult[0]:
            indvPlayerData.append(item)

        # teamID from player and use team reference table to get playerID
        teamIDData = (player[6],)
        cursor.execute(team_ref_query, teamIDData)
        oppTeamID = cursor.fetchall()

        oppTeamIDData = (player[7],)
        cursor.execute(team_ref_query, teamIDData)
        teamID = cursor.fetchall()

        # use teamID + date ID to query the team data and opp team data for that date
        # append to master array
        idTeam = 0
        for team in teamID:
            idTeam = team[0]

        idOppTeam = 0
        for oppTeam in oppTeamID:
            idOppTeam = oppTeam[0]

        teamQuery = (player[1], idTeam)
        cursor.execute(getTeamData, teamQuery)
        teamResult = cursor.fetchall()

        oppTeamQuery = (player[1], idOppTeam)
        cursor.execute(getTeamData, oppTeamQuery)
        oppTeamResult = cursor.fetchall()

        for item in teamResult[0]:
            indvPlayerData.append(item)

        for item in oppTeamResult[0]:
            indvPlayerData.append(item)

        # use position + dateID + opp team ID to query team vs. defense for that position
        # append to master array
        # doubl'n it!
        if player[4] == 'PG':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()

            for item in ball_handlers_results[0]:
                indvPlayerData.append(item)
            for item in ball_handlers_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'SG':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()

            for item in ball_handlers_results[0]:
                indvPlayerData.append(item)
            for item in wings_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'SF':
            pos_data = (str(int(player[1])), idOppTeam)
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for item in wings_results[0]:
                indvPlayerData.append(item)
            for item in bigs_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'PF':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for item in bigs_results[0]:
                indvPlayerData.append(item)
            for item in bigs_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'C':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_centers, pos_data)
            centers_results = cursor.fetchall()

            for item in centers_results[0]:
                indvPlayerData.append(item)
            for item in centers_results[0]:
                indvPlayerData.append(item)

        allPlayerFeatures.append(indvPlayerData)

    FDTargets = []
    DKTargets = []
    for player in playersPlaying:
        # last - append fanduel points + draftkings points
        indvPlayerFDTarget = player[8]
        FDTargets.append(indvPlayerFDTarget)
        indvPlayerDKTarget = player[9]
        DKTargets.append(indvPlayerDKTarget)

    # turn into numpy arrays
    numFeatures = len(allPlayerFeatures[0])
    testX = np.asarray(allPlayerFeatures)
    testY = np.asarray(FDTargets)

    print "Number of training examples: " + str(np.shape(testX)[0])

    # add bias term
    ones = np.ones((np.shape(testX)[0], 1), dtype=float)
    testX = np.hstack((ones, testX))

    # learning rate + iterations
    alpha = 0.01
    num_iters = 1000

    # theta initialization
    theta = np.zeros(((numFeatures + 1), 1))
    theta = np.transpose(theta)

    coefficents = TemporaryFile()

    ridge = Ridge(alpha=1, fit_intercept=False, normalize=True)
    ridge.fit(testX, testY)
    thetaSKLearnRidge = ridge.coef_

    outfile = open('coef.npz', 'w')
    np.save(outfile, thetaSKLearnRidge)

    print "Player Theta Values from Sklearn Ridge Regression"
    print thetaSKLearnRidge