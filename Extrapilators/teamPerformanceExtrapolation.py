import mysql.connector
import threading

cursorL = threading.RLock()

def averaging(cursor, performanceData, averageStatement, insertAvgStatement, tableID, team, date):
    cursor.execute(averageStatement, performanceData)

    new_cumlative = []
    cumulativeP = cursor.fetchall()

    if cumulativeP[0][5] == None:
        return  # when there is no results don't insert

    new_cumlative.append(tableID)
    new_cumlative.append(team)
    new_cumlative.append(date)
    for item in cumulativeP[0]:
        new_cumlative.append(item)

    cursor.execute(insertAvgStatement, new_cumlative)

# extrapolate daily team performance
def team_daily_extrapolate_data(cursor, dates, teams, cnx):
    # now loop, average, and insert
    average = 'select sum(win), sum(loss), avg(offensiveRating), avg(defensiveRating), avg(pointsAllowed), avg(pointsScored), avg(pace), avg(effectiveFieldGoalPercent), avg(turnoverPercent), avg(offensiveReboundPercent), avg(FTperFGA), avg(FG), avg(FGA), avg(FGP), avg(3P), avg(3PA), avg(3PP), avg(FT), avg(FTA), avg(FTP), avg(offensiveRebounds), avg(defensiveRebounds), avg(totalRebounds), avg(assists), avg(steals), avg(blocks), avg(turnovers), avg(personalFouls), avg(trueShootingPercent), avg(3pointAttemptRate), avg(freeThrowAttemptRate), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(points1Q), avg(points2Q), avg(points3Q), avg(points4Q) from team_performance where dailyTeamID = %s and dateID > 1247 and dateID < %s'

    insertAvg = "INSERT INTO team_daily_avg_performance VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    daily_id = 0

    cursorL.acquire()
    # give table id because you can't insert all without it
    getLastID = "Select MAX(dailyAvgPerformanceID) from team_daily_avg_performance"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 1

    cursorL.release()

    for date in dates:
        for team in teams:
            cursorL.acquire()

            performanceData = (team, date)

            averaging(cursor, performanceData, average, insertAvg, tableID, team, date)

            tableID = tableID + 1

            cnx.commit()

            cursorL.release()


def team_daily_extrapolate_two_one_data(cursor, dates, teams, cnx):
    # now loop, average, and insert
    average = 'select sum(win), sum(loss), avg(offensiveRating), avg(defensiveRating), avg(pointsAllowed), avg(pointsScored), avg(pace), avg(effectiveFieldGoalPercent), avg(turnoverPercent), avg(offensiveReboundPercent), avg(FTperFGA), avg(FG), avg(FGA), avg(FGP), avg(3P), avg(3PA), avg(3PP), avg(FT), avg(FTA), avg(FTP), avg(offensiveRebounds), avg(defensiveRebounds), avg(totalRebounds), avg(assists), avg(steals), avg(blocks), avg(turnovers), avg(personalFouls), avg(trueShootingPercent), avg(3pointAttemptRate), avg(freeThrowAttemptRate), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(points1Q), avg(points2Q), avg(points3Q), avg(points4Q) from team_performance where dailyTeamID = %s and dateID > %s and dateID < %s'

    insertAvg = "INSERT INTO team_two_one_daily_avg_performance VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    daily_id = 0

    cursorL.acquire()
    # give table id because you can't insert all without it
    getLastID = "Select MAX(dailyAvgPerformanceID) from team_two_one_daily_avg_performance"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 1

    cursorL.release()

    for date in dates:
        for team in teams:
            cursorL.acquire()

            twoOneDateID = date - 21

            performanceData = (team, twoOneDateID, date)

            averaging(cursor, performanceData, average, insertAvg, tableID, team, date)

            tableID = tableID + 1

            cnx.commit()

            cursorL.release()

def team_daily_extrapolate_seven_data(cursor, dates, teams, cnx):
    # now loop, average, and insert
    average = 'select sum(win), sum(loss), avg(offensiveRating), avg(defensiveRating), avg(pointsAllowed), avg(pointsScored), avg(pace), avg(effectiveFieldGoalPercent), avg(turnoverPercent), avg(offensiveReboundPercent), avg(FTperFGA), avg(FG), avg(FGA), avg(FGP), avg(3P), avg(3PA), avg(3PP), avg(FT), avg(FTA), avg(FTP), avg(offensiveRebounds), avg(defensiveRebounds), avg(totalRebounds), avg(assists), avg(steals), avg(blocks), avg(turnovers), avg(personalFouls), avg(trueShootingPercent), avg(3pointAttemptRate), avg(freeThrowAttemptRate), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(points1Q), avg(points2Q), avg(points3Q), avg(points4Q) from team_performance where dailyTeamID = %s and dateID > %s and dateID < %s'

    insertAvg = "INSERT INTO team_seven_daily_avg_performance VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    daily_id = 0
    # give table id because you can't insert all without it
    getLastID = "Select MAX(dailyAvgPerformanceID) from team_seven_daily_avg_performance"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0])
    tableID += 1

    cursorL.release()

    for date in dates:
        for team in teams:
            cursorL.acquire()

            sevenDateID = date - 7

            performanceData = (team, sevenDateID, date)

            averaging(cursor, performanceData, average, insertAvg, tableID, team, date)

            tableID = tableID + 1

            cnx.commit()

            cursorL.release()
def auto(dateID, cnx, cursor):

    # get teams
    getTeamIDs = "SELECT teamID FROM team_reference"
    cursor.execute(getTeamIDs)

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


    a = threading.Thread(target=team_daily_extrapolate_data, args=(cursor, dates, teams, cnx))
    s = threading.Thread(target=team_daily_extrapolate_seven_data, args=(cursor, dates, teams, cnx))
    t = threading.Thread(target=team_daily_extrapolate_two_one_data, args=(cursor, dates, teams, cnx))

    a.start()
    s.start()
    t.start()

    a.join()
    s.join()
    t.join()

    cnx.commit()


