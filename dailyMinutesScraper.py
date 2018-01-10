from bs4 import BeautifulSoup
import urllib2
import csv
import demjson
import json
import requests
import mysql.connector
from datetime import timedelta, date
import constants
import urllib2
import datetime as dt


def rotogrinders_season_scraper():
	url = "https://rotogrinders.com/game-stats/nba-player?site=fanduel&range=season"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_season_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrinders_fourweeks_scraper():
	url = "https://rotogrinders.com/game-stats/nba-player?site=fanduel&range=4weeks"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_fourweeks_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrinders_minutes_scraper():
	url = "https://rotogrinders.com/projected-stats/nba-player"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_minutes_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrindersBasketball(url, csv_filename, stats):
	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page, "html.parser")

	file = open(csv_filename, 'w')
	for stat in stats:
		file.write(stat + ", ")
	file.write("\n")

	jsonData = soup.find_all('script')
	jsonData = jsonData[len(jsonData) -1]

	jsonData = jsonData.text

	junk,jsonData = jsonData.split("data =")
	jsonData = jsonData.lstrip()
	jsonData = jsonData.rstrip()

	jsonData = jsonData.split(";")
	jsonData = jsonData[0]

#	jsonData = jsonData[:-1]

        cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
        cursor = cnx.cursor(buffered=True)


	basketballData = demjson.decode(jsonData)

        selec_id = "select playerID from player_reference where nickName=\""

        # this is date id for today
        date = constants.minutesDateID  
        update = "UPDATE performance SET projMinutes = %s where dateID = %s and playerID = %s"
        for playerData in basketballData:
		nickName = playerData['player']['first_name'] + " " + playerData['player']['last_name']
                
                get_id = selec_id + nickName + "\""
                try:
                    cursor.execute(get_id)
                    player_id = cursor.fetchall()[0][0]
                    inserts = (playerData['minutes'],date, player_id)
                    cursor.execute(update, inserts)
                    cnx.commit()
                except:
                    player_id = nickName + "Failed"


		print nickName, playerData['minutes'], player_id

                '''
		team = playerData['team']
		pos = playerData['pos']
		salary = playerData['salary']
		gp = playerData['gp']
		mins = float(playerData['min']) / float(gp)
		reb = float(playerData['reb']) / float(gp)
		ast = float(playerData['ast']) / float(gp)
		stl = float(playerData['stl']) / float(gp)
		blk = float(playerData['blk']) / float(gp)
		to = float(playerData['to']) / float(gp)
		pts = float(playerData['pts']) / float(gp)
		usg = playerData['usg']
		fpts = playerData['fpts']
		fpts = float(fpts) / float(gp)
		fpts = round(fpts, 2)
                '''
        

        cursor.close()
        cnx.commit()
        cnx.close()





if __name__ == "__main__":
	rotogrinders_minutes_scraper()
