import numpy as np
from scipy import sparse
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


def projMagic(cursor):
    # week 2 lonzo ball data - feature, target - score
    # ..........
    # .......
    # week 4 day - lonzo ball's data - feature, target - ?

    projDate = getDate(constants.dayP, constants.monthP, constants.yearP, cursor)

    # add minutes constraint
    get_players = "Select playerID from performance where dateID = %s"
    getDailyPlayerAvg = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_daily_avg WHERE dateID = %s AND playerID = %s"
    getDailyPlayerAvgSeven = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_seven_daily_avg WHERE dateID = %s AND playerID = %s"
    getDailyPlayerAvgTwoOne = "SELECT blocks, points, steals, AST, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, oRebound, dRebound, minutes, FG, FGA, FGP, 3PA, 3PP, FTM, FTA, FTP, personalFouls, plusMinus, trueShootingP, eFG, freeThrowAttemptRate, 3PointAttemptRate, oReboundP, dReboundP, totalReboundP, ASTP, STP, BLKP, turnoverP, USG, oRating, dRating FROM player_two_one_daily_avg WHERE dateID = %s AND playerID = %s"
    getPerformanceDataForEachPlayer = "SELECT playerID, dateID, fanduel, draftkings, fanduelPosition, draftkingsPosition, team, opponent, fanduelPts, draftkingsPts FROM performance WHERE dateID = %s AND minutesPlayed IS NOT NULL and minutesPlayed >= 8 and projMinutes IS NOT NULL AND fanduel IS NOT NULL AND fanduelPosition IS NOT NULL"
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
    team_ref_query = "SELECT teamID FROM team_reference WHERE bbreff = %s"

    # execute command + load into numpy array
    playersPlaying = []

    projDateData = (projDate,)
    cursor.execute(getPerformanceDataForEachPlayer, projDateData)
    results = cursor.fetchall()
    for player in results:
        playersPlaying.append(player)

    # get daily_player_avg
    # get opp_team stats
    # get self_team stats
    # get opp_vs_player position states
    # from perfromance get fanduel point for taraget
    allPlayerFeatures = []
    actualPlayersPlaying = []

    print len(playersPlaying)

    for player in playersPlaying:
        print "Player ID: " + str(player[0])
        print "Date ID: " + str(player[1])

        checkPlayerDailyAvgData = (player[1], player[0])
        cursor.execute(getDailyPlayerAvgSeven, checkPlayerDailyAvgData)

        # check to see + skip to next player if not in set
        check = cursor.fetchall()
        if len(check) == 0:
            continue

        indvPlayerData = []
        indvPlayerData.append(1) # bias term
        indvPlayerData.append(player[2])
        basicQueryData = (player[1], player[0])
        cursor.execute(getDailyPlayerAvg, basicQueryData)

        playerDailyAvgResult = cursor.fetchall()

        # append playerDailyAvgResult to indvPlayerData
        for item in playerDailyAvgResult[0]:
            indvPlayerData.append(item)

        # append playerDailyAvgSevenResult to indvPlayerData
        cursor.execute(getDailyPlayerAvgSeven, basicQueryData)
        playerDailyAvgSevenResult = cursor.fetchall()

        for item in playerDailyAvgSevenResult[0]:
            indvPlayerData.append(item)

        # append playerDailyAvgTwoOneResult to indvPlayerData
        cursor.execute(getDailyPlayerAvgTwoOne, basicQueryData)
        playerDailyAvgTwoOneResult = cursor.fetchall()
        for item in playerDailyAvgTwoOneResult[0]:
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

        # use position + dateID + opp team ID to query team vs. defense for that position
        # append to master array
        # doubl'n it!
        if player[4] == 'PG':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()

            for item in ball_handlers_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_seven, pos_data)
            ball_handlers_seven_results = cursor.fetchall()

            for item in ball_handlers_seven_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_two_one, pos_data)
            ball_handlers_two_one_results = cursor.fetchall()

            for item in ball_handlers_two_one_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'SG':
            pos_data = (player[1], idOppTeam)

            cursor.execute(get_ball_handlers, pos_data)
            ball_handlers_results = cursor.fetchall()
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()

            for w, b in zip(ball_handlers_results[0], wings_results[0]):
                item = ((w + b) / 2)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_seven, pos_data)
            ball_handlers_seven_results = cursor.fetchall()
            cursor.execute(get_wings_two_one, pos_data)
            wings_seven_results = cursor.fetchall()

            for w, b in zip(wings_seven_results[0], ball_handlers_seven_results[0]):
                item = ((w + b) / 2)
                indvPlayerData.append(item)

            cursor.execute(get_ball_handlers_two_one, pos_data)
            ball_handlers_two_one_results = cursor.fetchall()
            cursor.execute(get_wings_two_one, pos_data)
            wings_two_one_results = cursor.fetchall()

            for w, b in zip(wings_two_one_results[0], ball_handlers_two_one_results[0]):
                item = (w + b) / 2
                indvPlayerData.append(item)

        if player[4] == 'SF':
            pos_data = (str(int(player[1])), idOppTeam)
            cursor.execute(get_wings, pos_data)
            wings_results = cursor.fetchall()
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for w, b in zip(wings_results[0], bigs_results[0]):
                item = (w + b) / 2
                indvPlayerData.append(item)

            cursor.execute(get_wings_seven, pos_data)
            wings_seven_results = cursor.fetchall()
            cursor.execute(get_bigs_seven, pos_data)
            bigs_seven_results = cursor.fetchall()

            for w, b in zip(wings_seven_results[0], bigs_seven_results[0]):
                item = (w + b) / 2
                indvPlayerData.append(item)

            cursor.execute(get_wings_two_one, pos_data)
            wings_two_one_results = cursor.fetchall()
            cursor.execute(get_bigs_two_one, pos_data)
            bigs_two_one_results = cursor.fetchall()

            for w, b in zip(wings_two_one_results[0], bigs_two_one_results[0]):
                item = (w + b) / 2
                indvPlayerData.append(item)

        if player[4] == 'PF':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_bigs, pos_data)
            bigs_results = cursor.fetchall()

            for item in bigs_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_bigs_seven, pos_data)
            bigs_seven_results = cursor.fetchall()

            for item in bigs_seven_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_bigs_two_one, pos_data)
            bigs_two_one_results = cursor.fetchall()

            for item in bigs_two_one_results[0]:
                indvPlayerData.append(item)

        if player[4] == 'C':
            pos_data = (player[1], idOppTeam)
            cursor.execute(get_centers, pos_data)
            centers_results = cursor.fetchall()

            for item in centers_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_centers_seven, pos_data)
            centers_seven_results = cursor.fetchall()

            for item in centers_seven_results[0]:
                indvPlayerData.append(item)

            cursor.execute(get_centers_two_one, pos_data)
            centers_two_one_results = cursor.fetchall()

            for item in centers_two_one_results[0]:
                indvPlayerData.append(item)

        allPlayerFeatures.append(indvPlayerData)
        actualPlayersPlaying.append(player)

    # initialize
    targetX = np.zeros((len(actualPlayersPlaying), len(allPlayerFeatures[0])))

    # populate
    for i in range(len(actualPlayersPlaying)):
        for j in range(len(allPlayerFeatures[0])):
            targetX[i][j] = allPlayerFeatures[i][j]

    print "Number of targets: " + str(np.shape(targetX)[0])

    outfile = open('coef.npz', 'r')
    thetaSKLearnRidge = np.load(outfile)


    # predict
    targetYSKLearnRidge = targetX.dot(np.transpose(thetaSKLearnRidge))

    # load predictions into database

    pID = 0
    numPlayers = len(actualPlayersPlaying)
    while pID < numPlayers:
        playerID = actualPlayersPlaying[pID][0]
        playerProjectionSKLearn = 0
        playerProjectionSKLearnP = 0
        playerProjectionSKLearnRidge = float(targetYSKLearnRidge[pID])
        playerProjectionSKLearnRidgeP = 0

        updateBattersDKPoints = "UPDATE performance SET fdPointsPredSKLin = %s, fdPointsPredSKLinP = %s, fdPointsSKLinPredRidge = %s, fdPointsSKLinPredRidgeP = %s WHERE dateID = %s AND playerID = %s"
        updateBatterDKPointsData = (
            playerProjectionSKLearn, playerProjectionSKLearnP, playerProjectionSKLearnRidge, playerProjectionSKLearnRidgeP,
            projDate, playerID)
        cursor.execute(updateBattersDKPoints, updateBatterDKPointsData)

        pID = pID + 1

    print "Predicted FD Points for Players"

    cursor.close()
    cnx.commit()
    cnx.close()

if __name__ == "__main__":
    print "Loading data..."

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    projMagic(cursor)