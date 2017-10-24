import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests

def player_daily_avg_extrapolate(cursor):
    getPlayerIDs = "SELECT playerID FROM player_reference"
    cursor.execute(getPlayerIDs)
    
    players = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        players.push(row[0])
     
    getDates = "SELECT iddates FROM new_dates"
    cursor.execute(getDates)
    
    dates = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.push(row[0])
     
    # now loop, average, and insert
    average = 'select avg(blocks), avg(points), avg(steals), avg(assists), avg(turnovers), avg(totalRebounds), avg(tripleDouble), avg(doubleDouble), avg(3PM), avg(offensiveRebound), avg(defensiveRebounds), avg(minutesPlayed), avg(fieldGoals), avg(fieldGoalsAttempted), avg(fieldGoalPercent), avg(3PA), avg(3PPercent), avg(FT), avg(FTA), avg(FTPercent), avg(personalFouls), avg(plusMinus), avg(trueShootingPercent), avg(effectiveFieldGoalPercent), avg(freeThrowAttemptRate), avg(3pointAttemptRate), avg(offensiveReboundPercent), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPerecent), avg(stealPercent), avg(blockPercent), avg(turnoverPercent), avg(usagePercent), avg(offensiveRating), avg(defensiveRating) from performance where playerID=%s and dateID<=%s'
    
    insertAvg = "INSERT INTO player_daily_avg VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    insertCheck = "SELECT playerID FROM player_daily_avg WHERE playerID = %s AND dateID = %s"
    
    for date in dates:
        for player in players:
            performanceData = (player, date)
            cursor.execute(average, performanceData)
            
            cumulativeP = cursor.fetchall() 
            cumulativeP = performanceData + cumulativeP
            
            cursor.execute(insertCheck, performanceData)
            if not cursor.rowcount:
                cursor.execute(insertAvg, cumulativeP)Clellan 

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)
    
    player_daily_avg_extrapolate(cursor)

    cursor.close()
    cnx.commit()
    cnx.close()

