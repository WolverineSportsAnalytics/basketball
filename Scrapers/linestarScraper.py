import mysql.connector
from datetime import date, datetime
import linestar
import threading
import time

'''
Queries
'''
playerReferenceQ = "SELECT playerID, linestarID FROM player_reference WHERE nickName = %s"
insertLinestarIDQ = "UPDATE player_reference SET linestarID = %s WHERE playerID = %s"
insertCompetitionQ = "INSERT INTO slates (dateID, compName, localCompID, games, gpp, doubleUP) VALUES (%s, %s, %s, %s, %s, %s)"
checkCompetitionQ = "SELECT idslates FROM slates WHERE localCompID = %s AND dateID = %s"
updateCompetitionQ = "UPDATE slates SET compName = %s, games = %s, gpp = %s, doubleUP = %s WHERE dateID = %s AND localCompID = %s"
playerReferenceBackupQ = "SELECT playerID FROM player_reference WHERE linestarID = %s"
checkPlayerOwnershipQ = "SELECT idPlayerOwnership FROM player_ownership WHERE playerID = %s AND dateID = %s AND competitionID = %s"
updatePlayerOwnershipQ = "UPDATE player_ownership SET percentOwned = %s WHERE dateID = %s AND playerID = %s AND competitionID = %s"
insertPlayerOwnershipQ = "INSERT INTO player_ownership (dateID, playerID, competitionID, percentOwned) VALUES (%s, %s, %s, %s)"
findGameQ = "SELECT iddates FROM new_dates WHERE date = %s"

'''
* Function to retrieve the WSA date for the database
'''
def getDate(day, month, year, cursor):
    findGameData = (date(year, month, day),)
    cursor.execute(findGameQ, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

'''
* Function to retrieve the date from Linestar
'''
def dateFromLineStarLibrary(date):
    datetime_object = datetime.strptime(date, "%Y-%m-%d")

    return datetime_object

def wsaDatabaseUpdateInsertOwnershipData(value, date, cursor):
    print('Inserting/Updating data for: ' + str(date.year) + "-" + str(date.month) + "-" + str(date.day))
    wsaDateID = getDate(date.day, date.month, date.year, cursor)

    insertedPlayers = 0
    updatedPlayers = 0
    insertedCompetitions = 0
    updatedCompetitions = 0
    insertedLinestarIDs = 0
    neededLinestarIDs = 0

    if wsaDateID != -1:
        competitions = value.compeitions
        badPlayers = {}
        for comp in competitions:
            checkCompetitionD = (int(comp.id), wsaDateID)
            cursor.execute(checkCompetitionQ, checkCompetitionD)

            databaseCompID = -1

            compResultsQ = cursor.fetchall()
            resultsCountS = cursor.rowcount
            if resultsCountS >= 1:
                databaseCompID = compResultsQ[0][0]
                updateCompetitionD = (comp.name, int(comp.games), int(comp.gpp), int(comp.doubleUp), wsaDateID, int(comp.id))
                cursor.execute(updateCompetitionQ, updateCompetitionD)
                updatedCompetitions += 1
            else:
                insertCompetitionD = (wsaDateID, comp.name, int(comp.id), int(comp.games), int(comp.gpp), int(comp.doubleUp))
                cursor.execute(insertCompetitionQ, insertCompetitionD)
                databaseCompID = cursor.lastrowid
                insertedCompetitions += 1

            for player in comp.players:
                playerReferenceD = (player.name,)
                cursor.execute(playerReferenceQ, playerReferenceD)

                wsaPlayerID = -1

                playerRefObj = cursor.fetchall()
                if cursor.rowcount < 1:
                    playerReferenceBackupD = (player.id,)
                    cursor.execute(playerReferenceBackupQ, playerReferenceBackupD)
                    playerRefObj = cursor.fetchall()
                    if cursor.rowcount < 1:
                        if player.id not in badPlayers:
                            print("Player with nickname: " + str(player.name) + " could not be inserted")
                            print("Player has linestar id: " + str(player.id))
                            badPlayers[player.id] = player.name
                            neededLinestarIDs += 1
                    else:
                        wsaPlayerID = playerRefObj[0][0]
                elif cursor.rowcount >= 1 and playerRefObj[0][1] is None:
                    wsaPlayerID = playerRefObj[0][0]
                    insertLinestarIDD = (player.id, wsaPlayerID)
                    cursor.execute(insertLinestarIDQ, insertLinestarIDD)
                    insertedLinestarIDs += 1
                else:
                    wsaPlayerID = playerRefObj[0][0]

                if wsaPlayerID >= 0:
                    checkPlayerOwnershipD = (wsaPlayerID, wsaDateID, databaseCompID)
                    cursor.execute(checkPlayerOwnershipQ, checkPlayerOwnershipD)
                    cursor.fetchall()
                    resultsCountP = cursor.rowcount

                    if resultsCountP >= 1:
                        updatePlayerOwnershipD = (player.owned, wsaDateID, wsaPlayerID, databaseCompID)
                        cursor.execute(updatePlayerOwnershipQ, updatePlayerOwnershipD)
                        updatedPlayers += 1
                    else:
                        insertPlayerOwnershipD = (wsaDateID, wsaPlayerID, databaseCompID, player.owned)
                        cursor.execute(insertPlayerOwnershipQ, insertPlayerOwnershipD)
                        insertedPlayers += 1

        print('Loaded data for: ' + str(date.year) + "-" + str(date.month) + "-" + str(date.day))
        print('Statistics: ')
        print('Inserted Players: ' + str(insertedPlayers))
        print('Updated Players: ' + str(updatedPlayers))
        print('Inserted Competitions: ' + str(insertedCompetitions))
        print('Updated Competitions: ' + str(updatedCompetitions))
        print('Inserted Linestar IDs: ' + str(insertedLinestarIDs))
        print('Needed Linestar IDs: ' + str(neededLinestarIDs))
    else:
        print('No data for: ' + str(date.year) + "-" + str(date.month) + "-" + str(date.day))

    cnx.commit()

def scrapeLineStarDay(dayIn):
    day = dayIn
    data = linestar.standard.fanduel_nba_own_date(day)
    return data

def scrapeLineStarRange(d1, d2):
    data = linestar.standard.fanduel_nba_own_date_range(d1, d2)
    return data

def keepConnectionAlive():
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        cnx.ping(reconnect=False, attempts=1, delay=0)
        time.sleep(5)

def processScrapingRange(cursor, data):
    for key, value in data.items():
        date = dateFromLineStarLibrary(key)
        wsaDatabaseUpdateInsertOwnershipData(value, date, cursor)

def processScrapingDay(cursor, day, data):
    wsaDatabaseUpdateInsertOwnershipData(data, day, cursor)

if __name__ == "__main__":
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    d1 = datetime(2019, 2, 14)

    t = threading.Thread(target=keepConnectionAlive)
    t.start()
    data = scrapeLineStarDay(d1)
    t.do_run = False
    t.join()

    processScrapingDay(cursor, d1, data)

    cursor.close()
    cnx.commit()
    cnx.close()