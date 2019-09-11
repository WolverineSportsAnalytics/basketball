import mysql.connector
import json
import constants
import csv
import traceback
from datetime import date
import requests
from bs4 import BeautifulSoup, Comment

'''
Fanduel scraper scrapes the fanduel csv and inserts into the performance table
'''

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

            cursor.commit()

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
                    cursor.commit()
                else:
                    print("Must manual insert fanduel id for: " + name)
            else:
                playerID = 0
                for id in cursor:
                    playerID = id[0]
                insertData = (row[1].strip(), playerID)
                cursor.execute(insertRotoguruID, insertData)
                cursor.commit()

    cursor.commit()
    cursor.close()

def insert_into_performance(cursor, cnx, dateID):
    #empty will be used to scrape from rotoguru csv

    getPlayerID = "select playerID from player_reference where nickName= %s"

    getTeamAbbrev = "SELECT wsa from team_reference where fanduel = %s"
    update_performance = "INSERT INTO performance (playerID, dateID, fanduel, team, opponent, fanduelPosition, projMinutes) VALUES (%s, %s, %s, %s, %s, %s, %s)"


    url = "https://www.rotowire.com/daily/tables/optimizer-nba.php?sport=NBA&site=FanDuel&projections=&type=main&slate=all"
    page = requests.get(url)

    players = json.loads(str(page.text)) # Load from JSON

    for player in players:
    	try:
                first_name = player['first_name']
                last_name = player['last_name']
                name = first_name + ' ' + last_name
                pos = player['position'] # pos
                team  = player['team']
		opp = str(player['opponent'])
                sal = player['salary']
                minutes = player['minutes']

		if opp[0] == '@':
			opp = opp[1:]

		if team == "CHA":
            		team = "CHO"
        	if team == "BKN":
            		team = "BRK"
		if opp == "CHA":
            		opp = "CHO"
        	if opp == "BKN":
            		opp = "BRK"
		
		getPlayerIDD = (name, )
        

        	cursor.execute(getPlayerID, getPlayerIDD)
		if cursor.rowcount == 0:
			print(name, " not in player reference")

                player_id = cursor.fetchall()[0][0]
        
		inserts = (
              		player_id,
              		dateID,
              		sal,
              		team,
              		opp,
              		pos,
                        minutes)
		cursor.execute(update_performance, inserts)
	except Exception as e:
		print(e)


    cnx.commit()

def auto(day, month, year):
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    dateID = getDate(day, month, year, cursor)
    insert_into_performance(cursor, cnx, dateID)

if __name__ == "__main__":
    # dateID = getDate(constants.dayP, constants.monthP, constants.yearP, cursor)
    insert_into_performance(" ", " ", 1258)

