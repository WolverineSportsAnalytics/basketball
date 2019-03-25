from datetime import date as wsadate
from datetime import timedelta
import mysql.connector
from pydfs_lineup_optimizer import *
import constants

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (wsadate(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for date in cursor:
        dateID = date[0]

    return dateID

def optimizeAndFill(day, month, year, model, cursor,cnx):
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
    elif model == "mlp":
        getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.mlpProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 and p.mlpProj IS NOT NULL"
    elif model == "ridge":
        getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.ridgeProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.ridgeProj IS NOT NULL AND p.ridgeProj > 0"
    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    players = cursor.fetchall()
    #print ("Number of players being considered: " + str(cursor.rowcount))
    if(len(players) == 0):
        return

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

    try:
        lineups = optimizer.optimize(n=numLineups)
    except:
        return

    count = 2

    modelStr = ""
    modelNum = 1

    try:
      for lineup in lineups:
        modelStr = model + str(modelNum)
        dateQuery = "INSERT INTO basketball.historic_lineups (dateID, date, model) VALUES (%s, %s, %s)"
        dateQueryT = (gameID, str(month) + "-" + str(day) + "-" + str(year), modelStr)
        cursor.execute(dateQuery, dateQueryT)
        cnx.commit()
        print "Inserting Lineup"

        # print(lineup)
        # print(lineup.fantasy_points_projection)
        # print(lineup.salary_costs)
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
            cnx.commit()

        for player in playerIDList:
            dkpoints = dkpoints + fdPointsDict[player]
            playerName = fdPlayersPoints[player]

            # print optimized lineups
            #print("Player Name: " + str(playerName) + "; Actual Points Scored: " + str(fdPointsDict[player]))

        #print("Total Points: " + str(dkpoints))
        insertTotals = "UPDATE historic_lineups SET projPointsLineup = %s, actualPointsLineup = %s WHERE dateID = %s AND model = %s"
        insertTotalsData = (lineup.fantasy_points_projection, dkpoints, gameID, modelStr)
        cursor.execute(insertTotals, insertTotalsData)
        #print("\n")

        modelNum += 1
    except:
        print "Cant Lineup Num Players = ", len(players)

if __name__ == "__main__":
    print("Loading data...")

    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)


    startYear = constants.startYearP
    startMonth = constants.startMonthP + 1
    startDay = constants.startDayP

    endYear = constants.endYearP
    endMonth = constants.endMonthP
    endDay = constants.endDayP

    start_date = wsadate(startYear, startMonth, startDay)
    end_date = wsadate(endYear, endMonth, endDay)

    # for single_date in daterange(start_date, end_date):
    #     print(single_date)
    #     optimizeAndFill(single_date.day, single_date.month, single_date.year, "LeBron", cursor)
    #     optimizeAndFill(single_date.day, single_date.month, single_date.year, "Lonzo", cursor)
    #     optimizeAndFill(single_date.day, single_date.month, single_date.year, "Simmons", cursor)

    for single_date in daterange(start_date, end_date):

        optimizeAndFill(single_date.day, single_date.month, single_date.year, "mlp", cursor, cnx)

    cursor.close()
    cnx.commit()
    cnx.close()
