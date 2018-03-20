import mysql.connector
import mysql.connector.pooling
import constants
import threading

cursorL = threading.RLock()

def averaging(cursor, performanceData, averageStatement, insertAvgStatement, tableID, player, date):
    cursor.execute(averageStatement, performanceData)
    new_cumlative = []
    cumulativeP = cursor.fetchall()
    new_cumlative.append(tableID)
    new_cumlative.append(player)
    new_cumlative.append(date)
    for item in cumulativeP[0]:
        new_cumlative.append(item)

    if new_cumlative[4] is None:
        return
    else:
        cursor.execute(insertAvgStatement, new_cumlative)

def player_total_avg(cursor, dates, players, cnx):
    # now loop, average, and insert
    average = 'select avg(blocks), avg(points), avg(steals), avg(assists), avg(turnovers), avg(totalRebounds), avg(tripleDouble), avg(doubleDouble), avg(3PM), avg(offensiveRebounds), avg(defensiveRebounds), avg(minutesPlayed), avg(fieldGoals), avg(fieldGoalsAttempted), avg(fieldGoalPercent), avg(3PA), avg(3PPercent), avg(FT), avg(FTA), avg(FTPercent), avg(personalFouls), avg(plusMinus), avg(trueShootingPercent), avg(effectiveFieldGoalPercent), avg(freeThrowAttemptRate), avg(3pointAttemptRate), avg(offensiveReboundPercent), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(turnoverPercent), avg(usagePercent), avg(offensiveRating), avg(defensiveRating) from performance where playerID=%s and dateID>850 and dateID < %s'

    insertAvg = "INSERT INTO player_daily_avg VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    #give table id because you can't insert all without it
    getLastID = "Select MAX(iddailyplayer) from player_daily_avg"
    cursor.execute(getLastID)
    tableID = int(cursor.fetchall()[0][0]) + 1

    cursorL.release()

    for date in dates:
        for player in players:
            cursorL.acquire()

            performanceData = (player, date)

            averaging(cursor, performanceData, average, insertAvg, tableID, player, date)

            cnx.commit()

            tableID = tableID + 1

            cursorL.release()

def player_seven_avg(cursor, dates, players, cnx):
    averageSeven = 'select avg(blocks), avg(points), avg(steals), avg(assists), avg(turnovers), avg(totalRebounds), avg(tripleDouble), avg(doubleDouble), avg(3PM), avg(offensiveRebounds), avg(defensiveRebounds), avg(minutesPlayed), avg(fieldGoals), avg(fieldGoalsAttempted), avg(fieldGoalPercent), avg(3PA), avg(3PPercent), avg(FT), avg(FTA), avg(FTPercent), avg(personalFouls), avg(plusMinus), avg(trueShootingPercent), avg(effectiveFieldGoalPercent), avg(freeThrowAttemptRate), avg(3pointAttemptRate), avg(offensiveReboundPercent), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(turnoverPercent), avg(usagePercent), avg(offensiveRating), avg(defensiveRating) from performance where playerID=%s and dateID > %s and dateID < %s'

    insertAvgSeven = "INSERT INTO player_seven_daily_avg VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    getLastIDSeven = "Select MAX(iddailysevenplayer) from player_seven_daily_avg"
    cursor.execute(getLastIDSeven)
    tableIDSeven = int(cursor.fetchall()[0][0]) + 1

    cursorL.release()

    for date in dates:
        for player in players:
            cursorL.acquire()

            sevenID = date - 7

            sevenPerformanceData = (player, sevenID, date)

            averaging(cursor, sevenPerformanceData, averageSeven, insertAvgSeven, tableIDSeven, player, date)

            cnx.commit()

            tableIDSeven = tableIDSeven + 1

            cursorL.release()

def player_two_one_avg(cursor, dates, players, cnx):
    averageTwoOne = 'select avg(blocks), avg(points), avg(steals), avg(assists), avg(turnovers), avg(totalRebounds), avg(tripleDouble), avg(doubleDouble), avg(3PM), avg(offensiveRebounds), avg(defensiveRebounds), avg(minutesPlayed), avg(fieldGoals), avg(fieldGoalsAttempted), avg(fieldGoalPercent), avg(3PA), avg(3PPercent), avg(FT), avg(FTA), avg(FTPercent), avg(personalFouls), avg(plusMinus), avg(trueShootingPercent), avg(effectiveFieldGoalPercent), avg(freeThrowAttemptRate), avg(3pointAttemptRate), avg(offensiveReboundPercent), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(turnoverPercent), avg(usagePercent), avg(offensiveRating), avg(defensiveRating) from performance where playerID=%s and dateID > %s and dateID < %s'

    insertAvgTwoOne = "INSERT INTO player_two_one_daily_avg VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cursorL.acquire()

    getLastIDTwoOne = "Select MAX(iddailytwooneplayer) from player_two_one_daily_avg"
    cursor.execute(getLastIDTwoOne)
    tableIDTwoOne = int(cursor.fetchall()[0][0]) + 1

    cursorL.release()

    for date in dates:
        for player in players:
            cursorL.acquire()

            twoOneID = date - 21

            twoOnePerformanceData = (player, twoOneID, date)

            averaging(cursor, twoOnePerformanceData, averageTwoOne, insertAvgTwoOne, tableIDTwoOne, player, date)

            cnx.commit()

            tableIDTwoOne = tableIDTwoOne + 1

            cursorL.release()


def auto(dateID):
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    cursorL = threading.RLock()

    getPlayerIDs = "SELECT playerID FROM player_reference"
    cursor.execute(getPlayerIDs)

    players = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        players.append(row[0])

    dateCutOff = dateID
    upperBoundCutOff = dateID

    getDates = "SELECT iddates FROM new_dates WHERE iddates >= %s AND iddates <= %s"
    getDatesD = (dateCutOff, upperBoundCutOff)
    cursor.execute(getDates, getDatesD)

    dates = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.append(row[0])

    print "Dates Length", len(dates)

    t = threading.Thread(target=player_total_avg, args=(cursor, dates, players, cnx))
    s = threading.Thread(target=player_seven_avg, args=(cursor, dates, players, cnx))
    o = threading.Thread(target=player_two_one_avg, args=(cursor, dates, players, cnx))

    t.start()
    s.start()
    o.start()

    t.join()
    s.join()
    o.join()

    cursor.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    cursorL = threading.RLock()

    getPlayerIDs = "SELECT playerID FROM player_reference"
    cursor.execute(getPlayerIDs)

    players = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        players.append(row[0])

    dateCutOff = constants.dailyPerformanceExtrapolationDateCutOff
    upperBoundCutOff = constants.extapolatorUpperBound

    getDates = "SELECT iddates FROM new_dates WHERE iddates >= %s AND iddates <= %s"
    getDatesD = (dateCutOff, upperBoundCutOff)
    cursor.execute(getDates, getDatesD)

    dates = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.append(row[0])

    t = threading.Thread(target=player_total_avg, args=(cursor, dates, players, cnx))
    s = threading.Thread(target=player_seven_avg, args=(cursor, dates, players, cnx))
    o = threading.Thread(target=player_two_one_avg, args=(cursor, dates, players, cnx))

    t.start()
    s.start()
    o.start()

    t.join()
    s.join()
    o.join()

    cursor.close()
    cnx.commit()
    cnx.close()

