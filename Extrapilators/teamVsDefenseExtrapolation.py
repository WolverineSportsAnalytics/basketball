import mysql.connector

import threading
from multiprocessing import *

blockIdx = 0
pointsIdx = 1
stealsIdx = 2
assistsIdx = 3
turnoversIdx = 4
totalRIdx = 5
tripleDoubleIdx = 6
doubleDoubleIdx = 7
threePMIdx = 8
threePAIdx = 9
offensiveReboundsIdx = 10
defensiveReboundsIdx = 11
minutesPlayedIdx = 12
fieldGoalsIdx = 13
fieldGoalsAttemptedIdx = 14
FTIdx = 15
FTAIdx = 16
usageIdx = 17
ortIdx = 18
drtIdx = 19
tStIdx = 20
eFGIdx = 21

cursorL = threading.RLock()

def averaging(cursor, team, dateLower, dateUpper, tableID, playasVsOpponentsScript, teamVsBallHandlersScript,
              teamVsWingsScript, teamVsBigsScript, teamVsCentersScript, cnx):
    # get all players who played vs that team before that day
    # separate players into the buckets aboved based on their position

    getPlayersVsOpponents = playasVsOpponentsScript
    insertTeamVsDefenseBallHandlers = teamVsBallHandlersScript
    insertTeamVsDefenseWings = teamVsWingsScript
    insertTeamVsDefenseBigs = teamVsBigsScript
    insertTeamVsDefenseCenters = teamVsCentersScript


    # get all ball handlers
    playerVsOpponentsData = (team, dateLower, dateUpper, 'PG')
    cursor.execute(getPlayersVsOpponents, playerVsOpponentsData)
    pointGuards = cursor.fetchall()

    playerVsOpponentsData = (team, dateLower, dateUpper, 'SG')
    cursor.execute(getPlayersVsOpponents, playerVsOpponentsData)
    shootingGuards = cursor.fetchall()

    playerVsOpponentsData = (team, dateLower, dateUpper, 'SF')
    cursor.execute(getPlayersVsOpponents, playerVsOpponentsData)
    smallForwards = cursor.fetchall()

    playerVsOpponentsData = (team, dateLower, dateUpper, 'PF')
    cursor.execute(getPlayersVsOpponents, playerVsOpponentsData)
    powerForward = cursor.fetchall()

    # get centers
    playerVsOpponentsData = (team, dateLower, dateUpper, 'C')
    cursor.execute(getPlayersVsOpponents, playerVsOpponentsData)
    centers = cursor.fetchall()

    ballHandlers = pointGuards + shootingGuards
    wings = shootingGuards + smallForwards
    bigs = powerForward + smallForwards

    players = {'ball_handlers': ballHandlers, 'wings': wings, 'bigs': bigs, 'centers': centers}
    for key, value in players.items():
        ##############################
        # for each player in bucket
        # (sum all stats / games played till that point)
        blocks = 0
        points = 0
        steals = 0
        assists = 0
        turnovers = 0
        totalRebounds = 0
        tripleDouble = 0
        doubleDouble = 0
        threePM = 0
        threePA = 0
        offensiveRebounds = 0
        defensiveRebounds = 0
        minutesPlayed = 0
        fieldGoals = 0
        fieldGoalsAttempted = 0
        FT = 0
        FTA = 0
        usagePercent = 0
        offensiveRating = 0
        defensiveRating = 0
        trueShootingPercent = 0
        effectiveFieldGoalPercent = 0

        # unlazy but position = ballHandler
        for ballHandler in value:
            blocks = blocks + ballHandler[blockIdx]
            points = points + ballHandler[pointsIdx]
            steals = steals + ballHandler[stealsIdx]
            assists = assists + ballHandler[assistsIdx]
            turnovers = turnovers + ballHandler[turnoversIdx]
            totalRebounds = totalRebounds + ballHandler[totalRIdx]
            tripleDouble = tripleDouble + ballHandler[tripleDoubleIdx]
            doubleDouble = doubleDouble + ballHandler[doubleDoubleIdx]
            threePM = threePM + ballHandler[threePMIdx]
            threePA = threePA + ballHandler[threePAIdx]
            offensiveRebounds = offensiveRebounds + ballHandler[offensiveReboundsIdx]
            defensiveRebounds = defensiveRebounds + ballHandler[defensiveReboundsIdx]
            minutesPlayed = minutesPlayed + ballHandler[minutesPlayedIdx]
            fieldGoals = fieldGoals + ballHandler[fieldGoalsIdx]
            fieldGoalsAttempted = fieldGoalsAttempted + ballHandler[fieldGoalsAttemptedIdx]
            FT = FT + ballHandler[FTIdx]
            FTA = FTA + ballHandler[FTAIdx]
            usagePercent = usagePercent + ballHandler[usageIdx]
            offensiveRating = offensiveRating + ballHandler[ortIdx]
            defensiveRating = defensiveRating + ballHandler[drtIdx]
            trueShootingPercent = trueShootingPercent + ballHandler[tStIdx]
            effectiveFieldGoalPercent = effectiveFieldGoalPercent + ballHandler[eFGIdx]

        blocksPerMinute = float(blocks) / minutesPlayed if minutesPlayed else 0
        pointsPerMinute = float(points) / minutesPlayed if minutesPlayed else 0
        stealsPerMinute = float(steals) / minutesPlayed if minutesPlayed else 0
        assistsPerMinute = float(assists) / minutesPlayed if minutesPlayed else 0
        turnoversPerMinute = float(turnovers) / minutesPlayed if minutesPlayed else 0
        tripleDoubles = float(tripleDouble) / len(ballHandlers) if len(ballHandlers) else 0
        doubleDoubles = float(doubleDouble) / len(ballHandlers) if len(ballHandlers) else 0
        threePP = float(threePM) / float(threePA) if threePA else 0
        offensiveReboundsPerMinute = float(offensiveRebounds) / minutesPlayed if minutesPlayed else 0
        defensiveReoundsPerMinute = float(defensiveRebounds) / minutesPlayed if minutesPlayed else 0
        fieldGoalP = float(fieldGoals) / float(fieldGoalsAttempted) if fieldGoalsAttempted else 0
        FTP = float(FT) / float(FTA) if FTA else 0
        usagePercentTot = usagePercent / len(ballHandlers) if len(ballHandlers) else 0
        offensiveRatingTot = offensiveRating / len(ballHandlers) if len(ballHandlers) else 0
        defensiveRatingTot = defensiveRating / len(ballHandlers) if len(ballHandlers) else 0
        trueShooting = points / (2 * (float(fieldGoalsAttempted) + 0.44 * FTA)) if fieldGoalsAttempted else 0
        effectiveFieldGoal = (float(fieldGoals) + 0.5 * float(threePM)) / float(
            fieldGoalsAttempted) if fieldGoalsAttempted else 0

        # get team id
        teamIDQ = "SELECT teamID FROM team_reference WHERE bbreff = %s"
        teamIDD = (team,)
        cursor.execute(teamIDQ, teamIDD)

        teamID = 0
        for id in cursor.fetchall():
            teamID = id[0]

    
        teamVsPlayerData = (tableID, teamID, dateUpper, blocks, points, steals, assists, turnovers, totalRebounds,
                            tripleDouble, doubleDouble,
                            threePM, threePA, offensiveRebounds, defensiveRebounds, minutesPlayed, fieldGoals,
                            fieldGoalsAttempted, FT, FTA, blocksPerMinute, pointsPerMinute, stealsPerMinute,
                            assistsPerMinute, turnoversPerMinute, tripleDoubles, doubleDoubles, threePP,
                            offensiveReboundsPerMinute, defensiveReoundsPerMinute, fieldGoalP, FTP,
                            usagePercentTot,
                            offensiveRatingTot, defensiveRatingTot, trueShooting, effectiveFieldGoal)

        if key == 'ball_handlers':
            cursor.execute(insertTeamVsDefenseBallHandlers, teamVsPlayerData)
        if key == 'wings':
            cursor.execute(insertTeamVsDefenseWings, teamVsPlayerData)
        if key == 'bigs':
            cursor.execute(insertTeamVsDefenseBigs, teamVsPlayerData)
        if key == 'centers':
            cursor.execute(insertTeamVsDefenseCenters, teamVsPlayerData)

        cnx.commit()

def team_vs_defense_seven_extrapolation(cursor, dates, teams, cnx):
    performanceAvgScript = "SELECT blocks, points, steals, assists, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, 3PA, offensiveRebounds, defensiveRebounds, minutesPlayed, fieldGoals, fieldGoalsAttempted, FT, FTA, usagePercent, offensiveRating, defensiveRating, trueShootingPercent, effectiveFieldGoalPercent FROM performance WHERE opponent = %s AND dateID > %s AND dateID < %s AND fanduelPosition = %s"
    insertTeamVsDefenseBallHandlers = "INSERT INTO team_seven_vs_ball_handlers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseWings = "INSERT INTO team_seven_vs_wings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseBigs = "INSERT INTO team_seven_vs_bigs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseCenters = "INSERT INTO team_seven_vs_centers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    getLastID = "Select MAX(teamID) from team_seven_vs_centers"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 100

    cursorL.release()

    for date in dates:
        print date
        for team in teams:
            cursorL.acquire()

            averaging(cursor, team, (date - 7), date, tableID, performanceAvgScript, insertTeamVsDefenseBallHandlers,
                      insertTeamVsDefenseWings, insertTeamVsDefenseBigs, insertTeamVsDefenseCenters, cnx)

            tableID = tableID + 1

            cursorL.release()

def team_vs_defense_two_one_extrapolation(cursor, dates, teams, cnx):
    # iterate through all teams and all dates
    performanceAvgScript = "SELECT blocks, points, steals, assists, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, 3PA, offensiveRebounds, defensiveRebounds, minutesPlayed, fieldGoals, fieldGoalsAttempted, FT, FTA, usagePercent, offensiveRating, defensiveRating, trueShootingPercent, effectiveFieldGoalPercent FROM performance WHERE opponent = %s AND dateID > %s AND dateID < %s AND fanduelPosition = %s"
    insertTeamVsDefenseBallHandlers = "INSERT INTO team_two_one_vs_ball_handlers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseWings = "INSERT INTO team_two_one_vs_wings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseBigs = "INSERT INTO team_two_one_vs_bigs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseCenters = "INSERT INTO team_two_one_vs_centers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    getLastID = "Select MAX(teamID) from team_two_one_vs_centers"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 100

    cursorL.release()

    for date in dates:
        print date
        for team in teams:
            cursorL.acquire()

            averaging(cursor, team, (date - 21), date, tableID, performanceAvgScript, insertTeamVsDefenseBallHandlers,
                      insertTeamVsDefenseWings, insertTeamVsDefenseBigs, insertTeamVsDefenseCenters, cnx)

            tableID = tableID + 1

            cursorL.release()

def team_vs_defense_extrapolation(cursor, dates, teams, cnx):
    # iterate through all teams and all dates

    performanceAvgScript = "SELECT blocks, points, steals, assists, turnovers, totalRebounds, tripleDouble, doubleDouble, 3PM, 3PA, offensiveRebounds, defensiveRebounds, minutesPlayed, fieldGoals, fieldGoalsAttempted, FT, FTA, usagePercent, offensiveRating, defensiveRating, trueShootingPercent, effectiveFieldGoalPercent FROM performance WHERE opponent = %s AND dateID > %s AND dateID < %s AND fanduelPosition = %s"
    insertTeamVsDefenseBallHandlers = "INSERT INTO team_vs_ball_handlers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseWings = "INSERT INTO team_vs_wings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseBigs = "INSERT INTO team_vs_bigs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertTeamVsDefenseCenters = "INSERT INTO team_vs_centers VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    getLastID = "Select MAX(teamID) from team_vs_centers"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 100

    cursorL.release()

    beginningSeasonID = 1248

    for date in dates:
        print date
        for team in teams:
            cursorL.acquire()

            averaging(cursor, team, beginningSeasonID, date, tableID, performanceAvgScript, insertTeamVsDefenseBallHandlers,
                      insertTeamVsDefenseWings, insertTeamVsDefenseBigs, insertTeamVsDefenseCenters, cnx)

            tableID = tableID + 1

            cursorL.release()
def auto(dateID, cnx, cursor):

    # team vs. position

    # ball handlers
    # PG, SG

    # wings
    # SG, SF

    # bigs
    # SF, PF

    # centers
    # C

    '''
    for ball_handlers
    avg pts, rebounds, offensive stats defensive stats etc....
    for every player that has played vs that team before or on that date

    for all teams:
        get all players who played pg, sg, sf vs that team
            average their performances noe

    '''

    # get all teams
    getBbreffs = "SELECT bbreff FROM team_reference"
    cursor.execute(getBbreffs)

    teams = []

    sqlResults = cursor.fetchall()
    for row in sqlResults:
        teams.append(row[0])

    dateCutOff = dateID 
    upperBoundCutOff = dateID

    getDates = "SELECT iddates FROM new_dates WHERE iddates >= %s AND iddates <= %s"
    getDatesD = (dateCutOff, upperBoundCutOff)
    cursor.execute(getDates, getDatesD)

    dates = []

    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.append(row[0])

    a = threading.Thread(target=team_vs_defense_extrapolation, args=(cursor, dates, teams, cnx))
    s = threading.Thread(target=team_vs_defense_two_one_extrapolation, args=(cursor, dates, teams,cnx))
    t = threading.Thread(target=team_vs_defense_seven_extrapolation, args=(cursor, dates, teams, cnx))

    a.start()
    s.start()
    t.start()

    a.join()
    s.join()
    t.join()

    cnx.commit()
