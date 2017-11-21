import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests

# extrapolate daily team performance
def team_daily_extrapolate_data(cursor):
    # get teams
    getTeamIDs = "SELECT teamID FROM team_reference"
    cursor.execute(getTeamIDs)

    teams = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        teams.append(row[0])

    dateCutOff = constants.teamPerformanceExtrapolationDateCutOff

    getDates = "SELECT iddates FROM new_dates WHERE iddates >= %s"
    getDatesD = (dateCutOff, )
    cursor.execute(getDates, getDatesD)

    dates = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.append(row[0])

    # now loop, average, and insert
    average = 'select sum(win), sum(loss), avg(offensiveRating), avg(defensiveRating), avg(pointsAllowed), avg(pointsScored), avg(pace), avg(effectiveFieldGoalPercent), avg(turnoverPercent), avg(offensiveReboundPercent), avg(FTperFGA), avg(FG), avg(FGA), avg(FGP), avg(3P), avg(3PA), avg(3PP), avg(FT), avg(FTA), avg(FTP), avg(offensiveRebounds), avg(defensiveRebounds), avg(totalRebounds), avg(assists), avg(steals), avg(blocks), avg(turnovers), avg(personalFouls), avg(trueShootingPercent), avg(3pointAttemptRate), avg(freeThrowAttemptRate), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(points1Q), avg(points2Q), avg(points3Q), avg(points4Q) from team_performance where dailyTeamID = %s and dateID < %s'

    insertAvg = "INSERT INTO team_daily_avg_performance VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    insertCheck = "SELECT dailyTeamID FROM team_performance WHERE dailyTeamID = %s AND dateID = %s"

    daily_id = 0
    # give table id because you can't insert all without it
    tableID = 1
    for date in dates:
        for team in teams:
            performanceData = (team, date)
            cursor.execute(average, performanceData)

            new_cumlative = []
            cumulativeP = cursor.fetchall()
            
            if cumulativeP[0][5] == None:
                    continue # when there is no results don't insert
           
            new_cumlative.append(daily_id)
            new_cumlative.append(tableID)
            new_cumlative.append(team)
            new_cumlative.append(date)
            for item in cumulativeP[0]:
                new_cumlative.append(item)

            
            
            cursor.execute(insertAvg, new_cumlative)
            tableID = tableID + 1


            cnx.commit()


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    team_daily_extrapolate_data(cursor)

    cursor.close()
    cnx.commit()
    cnx.close()
