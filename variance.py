import mysql.connector
import constants
import csv
import traceback
from datetime import date

def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

def alignPlayerIDs(cursor):
    selec_id = "select playerID from player_reference where firstName= %s and lastName = %s"
    select_idTwo = "SELECT playerID from player_reference where nickName=%s"

    insertRotoguruID = "UPDATE player_reference SET fanduelID = %s WHERE playerID = %s"

    with open(constants.fanduelFileLocation, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in reader:
            # if they don't play don't consider them
            firstName = row[2]
            firstName = firstName.strip()
            lastName = row[4]
            lastName = lastName.strip()
            selectData = (firstName, lastName)
            cursor.execute(selec_id, selectData)
            if not cursor.rowcount:
                name = row[3]
                nameData = (name,)
                cursor.execute(select_idTwo, nameData)
                if cursor.rowcount:
                    playerID = 0
                    for id in cursor:
                        playerID = id[0]
                    insertData = (row[0].strip(), playerID)
                    cursor.execute(insertRotoguruID, insertData)
                    cnx.commit()
                else:
                    print "Must manual insert fanduel id for: " + name
            else:
                playerID = 0
                for id in cursor:
                    playerID = id[0]
                insertData = (row[0].strip(), playerID)
                cursor.execute(insertRotoguruID, insertData)
                cnx.commit()

    cursor.close()
    cnx.commit()
    cnx.close()

def insert_into_performance(cursor, cnx):
    #empty will be used to scrape from rotoguru csv

    getPlayerID = "select playerID from player_reference where fanduelID = %s"

    getTeamAbbrev = "SELECT wsa from team_reference where fanduel = %s"
    update_performance = "INSERT INTO performance (playerID, dateID, fanduel, team, opponent, fanduelPosition) VALUES (%s, %s, %s, %s, %s, %s)"

    dateID = getDate(constants.dayP, constants.monthP, constants.yearP, cursor)

    with open(constants.fanduelFileLocation, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[11] != 'O':
                try:
                    fanduelTempID = row[0]
                    getPlayerIDD = (fanduelTempID, )
                    cursor.execute(getPlayerID, getPlayerIDD)

                    if not cursor.rowcount:
                        print ("Did not insert into performance table for " + str(row[3]))

                    else:
                        player_id = cursor.fetchall()[0][0]

                        teamHomeAbbrevData = (row[9], )
                        cursor.execute(getTeamAbbrev, teamHomeAbbrevData)
                        homeTeam = cursor.fetchall()[0][0]

                        teamAwayAbbrevData = (row[10], )
                        cursor.execute(getTeamAbbrev, teamAwayAbbrevData)
                        awayTeam = cursor.fetchall()[0][0]

                        inserts = (
                            player_id,
                            dateID,
                            int(row[7]),
                            homeTeam,
                            awayTeam,
                            row[1])

                        cursor.execute(update_performance, inserts)

                except:
                    traceback.print_exc()
                    print row[3]

                cnx.commit()

    cursor.close()
    cnx.commit()
    cnx.close()

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)
    # alignPlayerIDs(cursor)
    insert_into_performance(cursor, cnx)

