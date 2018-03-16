import mysql.connector
import constants
import csv
from datetime import date

def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

def fixFanduelIDs(cursor):
    getFDIds = "select playerID, fanduelID FROM player_reference WHERE fanduelID IS NOT NULL"
    cursor.execute(getFDIds)

    insertFDIds = "UPDATE player_reference SET fanduelID = %s WHERE playerID = %s"

    results = cursor.fetchall()

    for player in results:
        fdID = player[1]
        pID = player[0]
        if fdID.find("-") != -1:
            fdDate, actualFDID = fdID.split("-")

            insertFDIdsD = (actualFDID, pID)
            cursor.execute(insertFDIds, insertFDIdsD)

            cnx.commit()

def alignPlayerIDs(cursor):
    selec_id = "select playerID from player_reference where firstName= %s and lastName = %s"
    select_idTwo = "SELECT playerID from player_reference where nickName=%s"

    insertRotoguruID = "UPDATE player_reference SET fanduelID = %s WHERE playerID = %s"

    with open(constants.fanduelFileLocation, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in reader:
            # if they don't play don't consider them
            firstName = row[3]
            firstName = firstName.strip()
            lastName = row[5]
            lastName = lastName.strip()
            selectData = (firstName, lastName)
            cursor.execute(selec_id, selectData)
            if not cursor.rowcount:
                name = row[4]
                nameData = (name,)
                cursor.execute(select_idTwo, nameData)
                if cursor.rowcount:
                    playerID = 0
                    for id in cursor:
                        playerID = id[0]
                    insertData = (row[1].strip(), playerID)
                    cursor.execute(insertRotoguruID, insertData)
                    cnx.commit()
                else:
                    print "Must manual insert fanduel id for: " + name
            else:
                playerID = 0
                for id in cursor:
                    playerID = id[0]
                insertData = (row[1].strip(), playerID)
                cursor.execute(insertRotoguruID, insertData)
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
    alignPlayerIDs(cursor)