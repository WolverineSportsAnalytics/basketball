from datetime import timedelta, date
import mysql.connector
import datetime as dt
import constants
import warnings
import requests

def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

def optimizeAndFill(day, month, year, model, cursor):
	gameID = getDate(day, month, year, cursor)

    # get players
    playas = []
    dkPointsDict = {}
    dkPlayersPoints = {}

    getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.leProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.leProj IS NOT NULL AND p.leProj > 0"
    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    print ("Number of players being considered: " + str(cursor.rowcount))
    players = cursor.fetchall()

    for baller in players:
        positions = []
        positions.append(str(baller[2]))
        dkPointsDict[baller[1]] = float(baller[7])
        dkPlayersPoints[baller[1]] = baller[0]

        newPlaya = Player(baller[1], baller[0], "", positions, baller[4], int(baller[5]), float(baller[3]))
        playas.append(newPlaya)

    #instantiate optimizer + run

    optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    optimizer.load_players(playas)

    # if duplicate player, increase n + generate next lineup,
    # next lineup will generate lineup with next highest amount of points
    numLineups = 1

    lineups = optimizer.optimize(n=numLineups)

    count = 2

    for lineup in lineups:
        print(lineup)
        print(lineup.fantasy_points_projection)
        print(lineup.salary_costs)
        playerIDList = []
        dkpoints = 0
        for player in lineup.lineup:
            playerIDList.append(player.id)
            if count == 1:
        		count += 1
	        else:
	        	count -= 1

		    posString = baller[2] + count
			# insert playerID, name, team, salary, projectedPoints
		    insertHistory = "INSERT INTO historic_lineups ("
		    insertHistory += posString + "playerID, "
		    insertHistory += posString + ", "
		    insertHistory += "team" + posString + ", "
		    insertHistory += "salary" + posString + ", "
		    insertHistory += "projPoints" + posString + ", "
		    insertHistory += "actualPoints" + posString + ")"
		    # VALUES (%s, %s, %s, %s, %s)"
		    insertHistoryT = (baller[1], baller[0], baller[4], baller[5], baller[3])
		    cursor.execute(insertHistory, insertHistoryT)

        for player in playerIDList:
            dkpoints = dkpoints + dkPointsDict[player]
            playerName = dkPlayersPoints[player]

            # print optimized lineups
            print("Player Name: " + str(playerName) + "; Actual Points Scored: " + str(dkPointsDict[player]))

        print("Total Points: " + str(dkpoints))
        print ("\n")

if __name__ == "__main__":
    print("Loading data...")

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    year = constants.yearP
    month = constants.monthP
    day = constants.dayP

    optimizeAndFill(day, month, year, "LeBron", cursor)
    optimizeAndFill(day, month, year, "Lonzo", cursor)
    optimizeAndFill(day, month, year, "Simmons", cursor)

    cursor.close()
    cnx.commit()
    cnx.close()