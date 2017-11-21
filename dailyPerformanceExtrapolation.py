import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests

def player_daily_avg_extrapolate(cursor, cnx):
    getPlayerIDs = "SELECT playerID FROM player_reference"
    cursor.execute(getPlayerIDs)
    
    players = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        players.append(row[0])

    dateCutOff = constants.dailyPerformanceExtrapolationDateCutOff
    lastTableID = constants.dailyPerformanceLastTableID

    getDates = "SELECT iddates FROM new_dates WHERE iddates >= %s"
    getDatesD = (dateCutOff, )
    cursor.execute(getDates, getDatesD)
    
    dates = []
    sqlResults = cursor.fetchall()
    for row in sqlResults:
        dates.append(row[0])
     
    # now loop, average, and insert
    average = 'select avg(blocks), avg(points), avg(steals), avg(assists), avg(turnovers), avg(totalRebounds), avg(tripleDouble), avg(doubleDouble), avg(3PM), avg(offensiveRebounds), avg(defensiveRebounds), avg(minutesPlayed), avg(fieldGoals), avg(fieldGoalsAttempted), avg(fieldGoalPercent), avg(3PA), avg(3PPercent), avg(FT), avg(FTA), avg(FTPercent), avg(personalFouls), avg(plusMinus), avg(trueShootingPercent), avg(effectiveFieldGoalPercent), avg(freeThrowAttemptRate), avg(3pointAttemptRate), avg(offensiveReboundPercent), avg(defensiveReboundPercent), avg(totalReboundPercent), avg(assistPercent), avg(stealPercent), avg(blockPercent), avg(turnoverPercent), avg(usagePercent), avg(offensiveRating), avg(defensiveRating) from performance where playerID=%s and dateID < %s'
    
    insertAvg = "INSERT INTO player_daily_avg VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    insertCheck = "SELECT playerID FROM player_daily_avg WHERE playerID = %s AND dateID = %s"

    #give table id because you can't insert all without it 
    tableID = lastTableID
    for date in dates:
	if date < 789:
	    continue
        for player in players:
            performanceData = (player, date)

	    # if returns none just skip it 
	    if new_cumlative[4] == None :
		    continue
            
	   
	    table_id = table_id + 1;
            cursor.execute(insertAvg, new_cumlative)
    	    
	    cursor.close()
	    cnx.commit()
	    cnx.close()
            cursor.execute(insertCheck, performanceData)

            if not cursor.rowcount:
                cursor.execute(average, performanceData)
                new_cumlative = []
                cumulativeP = cursor.fetchall()
                new_cumlative.append(tableID)
                new_cumlative.append(player)
                new_cumlative.append(date)
                for item in cumulativeP[0]:
                    new_cumlative.append(item)

                # if returns none just skip it
                if new_cumlative[4] == None:
                    continue
                cursor.execute(insertAvg, new_cumlative)
                tableID = tableID + 1

            cnx.commit()


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)
    
    player_daily_avg_extrapolate(cursor, cnx)

    cursor.close()
    cnx.commit()
    cnx.close()

