import mysql.connector
import constants
import csv

def alignPlayerIDs(cursor):
    selec_id = "select playerID from player_reference where firstName= %s and lastName = %s"
    select_idTwo = "SELECT playerID from player_reference where nickName=%s"

    insertRotoguruID = "UPDATE player_reference SET rotoguruID = %s WHERE playerID = %s"

    with open(constants.rotoguruFileLocation, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in reader:
            # if they don't play don't consider them
            if row[13] != 0:
                firstName = row[2]
                firstName = firstName.strip()
                lastName = row[1]
                lastName = lastName.strip()
                selectData = (firstName, lastName)
                cursor.execute(selec_id, selectData)
                if not cursor.rowcount:
                    name = firstName + " " + lastName
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
                        print "Must manual insert rotoguru id for: " + name
                else:
                    playerID = 0
                    for id in cursor:
                        playerID = id[0]
                    insertData = (row[0].strip(), playerID)
                    cursor.execute(insertRotoguruID, insertData)
                    cnx.commit()

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    alignPlayerIDs(cursor)

    cursor.close()
    cnx.commit()
    cnx.close()