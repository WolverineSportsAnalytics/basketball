from datetime import date
import mysql.connector
from pydfs_lineup_optimizer import *
from decimal import *
import numpy as np
import constants

def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

def optimize(day, month, year, cursor):

    gameID = getDate(day, month, year, cursor)

    # get players
    playas = []

    getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.fdPointsSKLinPredRidge, p.team, p.fanduel, p.opponent FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 10"
    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    numBatters = float(cursor.rowcount)
    print ("Number of players being considered: " + str(cursor.rowcount))
    players = cursor.fetchall()

    for baller in players:
        newPlaya = Player(baller[1], baller[0], "", baller[2], baller[4], int(baller[5]), float(baller[3]))
        playas.append(newPlaya)

    #instantiate optimizer + run

    optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    optimizer.load_players(playas)

    # if duplicate player, increase n + generate next lineup,
    # next lineup will generate lineup with next highest amount of points
    numLineups = 5
    lineups = optimizer.optimize(n=numLineups)

    for lineup in lineups:
        print ("Lineup #: " + str(lineupCounter))
        print(lineup)
        lineupCounter = lineupCounter + 1
        print ("\n")

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)

    cursor = cnx.cursor(buffered=True)

    year = constants.yearP
    month = constants.monthP
    day = constants.dayP

    # percentageOwnedandVarianceNormalization(day, month, year, cursor)
    optimize(day, month, year, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()