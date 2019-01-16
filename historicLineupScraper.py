from datetime import date
import mysql.connector
from pydfs_lineup_optimizer import *
import constants

def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for date in cursor:
        dateID = date[0]

    return dateID

def optimizeAndFill(day, month, year, model, cursor):
    gameID = getDate(day, month, year, cursor)

    # get players
    playas = []
    fdPointsDict = {}
    fdPlayersPoints = {}
    getPlayersQuery = ""

    if model == "LeBron":
        getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.leProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.leProj IS NOT NULL AND p.leProj > 0"
    elif model == "Lonzo":
        getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.zoProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.zoProj IS NOT NULL AND p.zoProj > 0"
    elif model == "Simmons":
        getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.simmonsProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.simmonsProj IS NOT NULL AND p.simmonsProj > 0"

    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    players = cursor.fetchall()
    print ("Number of players being considered: " + str(cursor.rowcount))

    for baller in players:
        positions = []
        positions.append(str(baller[2]))
        fdPointsDict[baller[1]] = float(baller[7])
        fdPlayersPoints[baller[1]] = baller[0]

        newPlaya = Player(baller[1], baller[0], "", positions, baller[4], int(baller[5]), float(baller[3]))
        playas.append(newPlaya)

    #instantiate optimizer + run

    optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    optimizer.load_players(playas)

    # if duplicate player, increase n + generate next lineup,
    # next lineup will generate lineup with next highest amount of points
    numLineups = 5

    lineups = optimizer.optimize(n=numLineups)

    count = 2

    modelStr = ""
    modelNum = 1

    for lineup in lineups:
        modelStr = model + str(modelNum)
        dateQuery = "INSERT INTO basketball.historic_lineups (dateID, date, model) VALUES (%s, %s, %s)"
        dateQueryT = (gameID, str(month) + "-" + str(day) + "-" + str(year), modelStr)
        cursor.execute(dateQuery, dateQueryT)

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

            if player.lineup_position != "C":
                posString = player.lineup_position + str(count)
            else:
                posString = "C"
            # insert playerID, name, team, salary, projectedPoints
            insertHistory = "UPDATE historic_lineups SET "
            insertHistory += posString + "playerID = %s, "
            insertHistory += posString + " = %s, "
            insertHistory += "team" + posString + " = %s, "
            insertHistory += "salary" + posString + " = %s, "
            insertHistory += "projPoints" + posString + " = %s, "
            insertHistory += "actualPoints" + posString + " = %s "
            insertHistory += "WHERE dateID = %s AND model = %s"
            # VALUES (%s, %s, %s, %s, %s)"
            insertHistoryT = (player.id, player.first_name, player.team, player.salary, player.fppg, fdPointsDict[player.id], gameID, modelStr)
            cursor.execute(insertHistory, insertHistoryT)

        for player in playerIDList:
            dkpoints = dkpoints + fdPointsDict[player]
            playerName = fdPlayersPoints[player]

            # print optimized lineups
            print("Player Name: " + str(playerName) + "; Actual Points Scored: " + str(fdPointsDict[player]))

        print("Total Points: " + str(dkpoints))
        insertTotals = "UPDATE historic_lineups SET projPointsLineup = %s, actualPointsLineup = %s WHERE dateID = %s AND model = %s"
        insertTotalsData = (lineup.fantasy_points_projection, dkpoints, gameID, modelStr)
        cursor.execute(insertTotals, insertTotalsData)
        print("\n")

        modelNum += 1

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
