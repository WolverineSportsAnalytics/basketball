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

'''
Pull in all features and insert into the futures 
'''

# goal is to populate the database with all the features

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
            # remove beginning 2 weeks of season + last week of season
            # for some reason team_seven_avg performance won't fill up all the way for dateID 801, 802, 803 - ahh b/c of all-star break
            # + 7 day period
            # or (game[0] >= 897 and game[0] <= 1052)) -> should have this!
            # (game[0] >= 695 and game[0] <= 795) -> should have this
            # (game[0] >= 804 and game[0] <= 843) -> should have this
            if ((((game[0] >= 695 and game[0] <= 738))
                and game[0] != 920 and game[0] != 711 and game[0] != 741)):
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

    # example of what this is doing
    # week 2 lonzo ball data - feature, target - score
    # ..........
    # .......
    # week 4 day - lonzo ball's data - feature, target - ?

    numpyDataArrays = []

    # add minutes constraint
    get_players = "Select playerID from performance where dateID = %s"
    getDailyPlayerAvg = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_daily_avg WHERE dateID = %s AND playerID = %s"
    getDailyPlayerAvgSeven = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_seven_daily_avg WHERE dateID = %s AND playerID = %s"
    getDailyPlayerAvgTwoOne = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_two_one_daily_avg WHERE dateID = %s AND playerID = %s"
    getPerformanceDataForEachPlayer = "SELECT playerID, dateID, fanduel, draftkings, fanduelPosition, draftkingsPosition, team, opponent, fanduelPts, draftkingsPts, projMinutes FROM performance WHERE dateID = %s AND minutesPlayed IS NOT NULL and minutesPlayed >= 8 and projMinutes IS NOT NULL AND fanduel IS NOT NULL AND fanduelPosition IS NOT NULL"
    getTeamData = "SELECT wins, losses, ORT, DRT, avgPointsAllowed, avgPointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, offensiveReboundPercent, FT/FGA, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, points1Q, points2Q, points3Q, points4Q FROM team_daily_avg_performance WHERE dateID = %s AND dailyTeamID = %s"
    getTeamDataSeven = "SELECT wins, losses, ORT, DRT, avgPointsAllowed, avgPointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, offensiveReboundPercent, FT/FGA, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, points1Q, points2Q, points3Q, points4Q FROM team_seven_daily_avg_performance WHERE dateID = %s AND dailyTeamID = %s"
    getTeamDataTwoOne = "SELECT wins, losses, ORT, DRT, avgPointsAllowed, avgPointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, offensiveReboundPercent, FT/FGA, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, points1Q, points2Q, points3Q, points4Q FROM team_two_one_daily_avg_performance WHERE dateID = %s AND dailyTeamID = %s"

    get_ball_handlers = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_ball_handlers WHERE dateID = %s and dailyTeamID = %s"
    get_ball_handlers_seven = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_seven_vs_ball_handlers WHERE dateID = %s and dailyTeamID = %s"
    get_ball_handlers_two_one = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_two_one_vs_ball_handlers WHERE dateID = %s and dailyTeamID = %s"
    get_wings = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_wings where dateID = %s and dailyTeamID = %s"
    get_wings_seven = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_seven_vs_wings where dateID = %s and dailyTeamID = %s"
    get_wings_two_one = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_two_one_vs_wings where dateID = %s and dailyTeamID = %s"
    get_bigs = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_bigs WHERE dateID = %s and dailyTeamID = %s"
    get_bigs_seven = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_seven_vs_bigs WHERE dateID = %s and dailyTeamID = %s"
    get_bigs_two_one = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_two_one_vs_bigs WHERE dateID = %s and dailyTeamID = %s"
    get_centers = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_vs_centers WHERE dateID = %s and dailyTeamID = %s"
    get_centers_seven = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_seven_vs_centers WHERE dateID = %s and dailyTeamID = %s"
    get_centers_two_one = "Select blocks, points, steals, assists, turnovers, tRebounds, DDD, DD, 3PM, 3PA, oRebounds, dRebounds, minutes, FG, FGA, FT, FTA, BPM, PPM, SPM, APM, TPM, DDDPG, DDPG, 3PP, ORPM, DRPM, FGP, FTP, usg, ORT, DRT, TS, eFG from team_two_one_vs_centers WHERE dateID = %s and dailyTeamID = %s"

    insert_features = "INSERT INTO futures VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
    playersActuallyPlaying = []
    features = ()
    print len(playersPlaying)
    getLastID = "Select MAX(idfeatures) from futures"
    cursor.execute(getLastID)
    feaID = int(cursor.fetchall()[0][0])
    feaID += 1
    for player in playersPlaying:
        print "Player ID: " + str(player[0])
        print "Date ID: " + str(player[1])

        checkPlayerDailyAvgData = (player[1], player[0])
        cursor.execute(getDailyPlayerAvgSeven, checkPlayerDailyAvgData)

        # check to see + skip to next player if not in set
        check = cursor.fetchall()
        if len(check) == 0:
            continue

        # player and date id for reference
        features = features + (feaID,)
        features = features + (player[0], player[1])

        # fanduel + dk salaries to features
        features = features + (player[2], 0)

        indvPlayerData = []
        indvPlayerData.append(player[2])
        basicQueryData = (player[1], player[0])
        cursor.execute(getDailyPlayerAvg, basicQueryData)

        playerDailyAvgResult = cursor.fetchall()

        # append playerDailyAvgResult to indvPlayerData
        for item in playerDailyAvgResult[0]:
            features = features + (item,)
            indvPlayerData.append(item)

        # append playerDailyAvgSevenResult to indvPlayerData
        cursor.execute(getDailyPlayerAvgSeven, basicQueryData)
        playerDailyAvgSevenResult = cursor.fetchall()

        for item in playerDailyAvgSevenResult[0]:
            features = features + (item,)
            indvPlayerData.append(item)

        # append playerDailyAvgTwoOneResult to indvPlayerData
        cursor.execute(getDailyPlayerAvgTwoOne, basicQueryData)
        playerDailyAvgTwoOneResult = cursor.fetchall()
        for item in playerDailyAvgTwoOneResult[0]:
            features = features + (item,)
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

        # get seven days team data
        cursor.execute(getTeamDataSeven, teamQuery)
        teamResultSeven = cursor.fetchall()

        for item in teamResultSeven[0]:
            indvPlayerData.append(item)

        # get two one days team data
        cursor.execute(getTeamDataTwoOne, teamQuery)
        teamDataTwoOne = cursor.fetchall()

        for item in teamDataTwoOne[0]:
            indvPlayerData.append(item)

        for n, s, t in zip(teamResult[0], teamResultSeven[0], teamDataTwoOne[0]):
            features = features + (n,s,t)

        # get opp team data
        for item in oppTeamResult[0]:
            indvPlayerData.append(item)

        # get seven days opp team data
        cursor.execute(getTeamDataSeven, oppTeamQuery)
        oppTeamResultSeven = cursor.fetchall()

        for item in oppTeamResultSeven[0]:
            indvPlayerData.append(item)

        # get two one days opp team data
        cursor.execute(getTeamDataTwoOne, oppTeamQuery)
        oppTeamDataTwoOne = cursor.fetchall()

        for item in oppTeamDataTwoOne[0]:
            indvPlayerData.append(item)

        for n, s, t in zip(oppTeamResult[0], oppTeamResultSeven[0], oppTeamDataTwoOne[0]):
            features = features + (n,s,t)

        # use position + dateID + opp team ID to query team vs. defense for that position
        # append to master array
        # doubl'n it!
        if player[4] == 'PG':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()

            for item in ball_handlers_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_seven, pos_data)
            ball_handlers_seven_results = cursor.fetchall()

            for item in ball_handlers_seven_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_two_one, pos_data)
            ball_handlers_two_one_results = cursor.fetchall()

            for item in ball_handlers_two_one_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

        if player[4] == 'SG':
            pos_data = (player[1], idOppTeam)

            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()

            for w, b in zip(ball_handlers_results[0], wings_results[0]):
                item = ((w + b) / 2)
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_seven, pos_data)
            ball_handlers_seven_results = cursor.fetchall()
            cursor.execute(get_wings_two_one, pos_data)
            wings_seven_results = cursor.fetchall()

            for w, b in zip(wings_seven_results[0], ball_handlers_seven_results[0]):
                item = ((w + b) / 2)
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_two_one, pos_data)
            ball_handlers_two_one_results = cursor.fetchall()
            cursor.execute(get_wings_two_one, pos_data)
            wings_two_one_results = cursor.fetchall()

            for w, b in zip(wings_two_one_results[0], ball_handlers_two_one_results[0]):
                item = (w + b) / 2
                features = features + (item,)
                indvPlayerData.append(item)

        if player[4] == 'SF':
            pos_data = (str(int(player[1])), idOppTeam)
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for w, b in zip(wings_results[0], bigs_results[0]):
                item = (w + b) / 2
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_wings_seven, pos_data)
            wings_seven_results = cursor.fetchall()
            cursor.execute(get_bigs_seven, pos_data)
            bigs_seven_results = cursor.fetchall()

            for w, b in zip(wings_seven_results[0], bigs_seven_results[0]):
                item = (w + b) / 2
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_wings_two_one, pos_data)
            wings_two_one_results = cursor.fetchall()
            cursor.execute(get_bigs_two_one, pos_data)
            bigs_two_one_results = cursor.fetchall()

            for w, b in zip(wings_two_one_results[0], bigs_two_one_results[0]):
                item = (w + b) / 2
                features = features + (item,)
                indvPlayerData.append(item)

        if player[4] == 'PF':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for item in bigs_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_bigs_seven, pos_data)
            bigs_seven_results = cursor.fetchall()

            for item in bigs_seven_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_bigs_two_one, pos_data)
            bigs_two_one_results = cursor.fetchall()

            for item in bigs_two_one_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

        if player[4] == 'C':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_centers, pos_data)
            centers_results = cursor.fetchall()

            for item in centers_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_centers_seven, pos_data)
            centers_seven_results = cursor.fetchall()

            for item in centers_seven_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

            cursor.execute(get_centers_two_one, pos_data)
            centers_two_one_results = cursor.fetchall()

            for item in centers_two_one_results[0]:
                features = features + (item,)
                indvPlayerData.append(item)

        allPlayerFeatures.append(indvPlayerData)

        # insert all features into database
        features = features + (player[10])
        features = features + (player[8], player[9])
        cursor.execute(insert_features, features)
        cnx.commit()
        feaID += 1
        features = ()
        playersActuallyPlaying.append(player)

    selectQuery = "SELECT playerID, dateID FROM futures WHERE fanduelPts IS NULL"
    selectPerformance = "SELECT fanduelPts, draftkingsPts FROM performance WHERE playerID = %s AND dateID = %s"

    insertFeature = "UPDATE futures SET fanduelPts = %s, draftkingsPts = %s WHERE playerID = %s AND dateID = %s"

    cursor.execute(selectQuery)

    playersPlayed = cursor.fetchall()

    for player in playersPlayed:
        pData = (player[0], player[1])
        cursor.execute(selectPerformance, pData)

        insertData = cursor.fetchall()

        insertDataT = (insertData[0][0], insertData[0][1], player[0], player[1])

        cursor.execute(insertFeature, insertDataT)
