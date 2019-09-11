from datetime import date
import mysql.connector
import datetime
import csv
from draftfast import rules
from draftfast.optimize import run
from draftfast.orm import Player
from draftfast.csv_parse import salary_download

'''
Pulls in our projections and the sallarys of current players and optimizing for the night
Optimizes using pydfs_lineup_optimizer
'''

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
    print(gameID)

    # get players
    playas = []
    dkPointsDict = {}
    dkPlayersPoints = {}

    getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.leProj, p.team, p.fanduel, p.opponent, p.fanduelPts, b.fanduelID FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.leProj IS NOT NULL AND p.leProj > 0"
    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    print ("Number of players being considered: " + str(cursor.rowcount))
    players = cursor.fetchall()

    # Create players
    player_pool = []

    for baller in players:
        positions = []
        positions.append(str(baller[2]))
        for pos in positions:
            newPlaya = Player(name=baller[0], cost=baller[5], proj=baller[3], pos=pos)
            player_pool.append(newPlaya)

    roster = run(
        rule_set=rules.FD_NBA_RULE_SET,
        player_pool=player_pool,
        verbose=True,
    )

if __name__ == "__main__":
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)



    now = datetime.datetime.now()
    day = now.day - 1
    year = now.year
    month = now.month

    optimize(day, month, year, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()