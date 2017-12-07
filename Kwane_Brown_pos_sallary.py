import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests
import csv
import traceback
def fd_pos_convert(pos):
    if pos == '1':
        return 'PG'
    if pos == '2':
        return 'SG'
    if pos == '3':
        return 'SF'
    if pos == '4':
        return 'PF'
    if pos == '5':
        return 'C'

def dk_pos_convert(pos):
    if len(pos) == 1:
        return fd_pos_convert(pos)
    elif len(pos) == 2:
        return fd_pos_convert(pos[0]) + '/' + fd_pos_convert(pos[1])

def date_convert(date):
    return date[:4] + "-" + date[4:6] + "-" + date[6:8]

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

def scrape_rotoguru(cursor, cnx):
    #empty will be used to scrape from rotoguru csv
    selec_id = "select playerID from player_reference where nickName=\""
    selec_date_id = "select iddates from new_dates where date=\""
    select_idTwo = "SELECT playerID from player_reference where RotoguruID=\""

    update_performance = "Update performance set fanduel=%s, draftkings=%s, fanduelPosition=%s, draftkingsPosition=%s where playerID=%s and dateID=%s"
    false = []
    with open(constants.rotoguruFileLocation, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in reader:
            if row[13] != 0:
                try:
                    name = row[3]
                    rot_id = row[0]
                    select_idTwos = select_idTwo + rot_id + "\""
                    cursor.execute(select_idTwos)
                    player_id = cursor.fetchall()[0][0]


                    date = row[4]
                    get_date = selec_date_id + date + "\""
                    cursor.execute(get_date)
                    date_id = cursor.fetchall()[0][0]


                    dk_salary = row[25]
                    fd_salary = row[23]
                    dk_pos = row[32]
                    dk_pos = dk_pos_convert(dk_pos)
                    fd_pos = row[31]
                    fd_pos = fd_pos_convert(fd_pos)

                    inserts = (
                        fd_salary,
                        dk_salary,
                        fd_pos,
                        dk_pos,
                        player_id,
                        date_id)


                    cursor.execute(update_performance,inserts)

                except:
                    traceback.print_exc()
                    print name
                    false.append(name)

                cnx.commit()

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    scrape_rotoguru(cursor, cnx)

    cursor.close()
    cnx.commit()
    cnx.close()
