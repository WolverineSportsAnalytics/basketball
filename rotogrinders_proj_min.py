from bs4 import BeautifulSoup
import urllib2
import csv
import demjson

'''
currently unfished
'''

def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP


def rotogrinders_daily_PMIN_scraper():
    url = "https://rotogrinders.com/projected-stats/nba-player"
    stats = [“Name”, "PMIN"]
    csv_filename = 'rotogrinders_season_basketball.csv'
    rotogrindersBasketball(url, csv_filename, stats)


def rotogrindersBasketball(url, csv_filename, stats):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page, "html.parser")

    jsonData = soup.find_all('script')[12]

    jsonData = jsonData.text

    junk, jsonData = jsonData.split("var data =")
    jsonData = jsonData.lstrip()
    jsonData = jsonData.rstrip()

    jsonData, junk = jsonData.split("var pageType =")
    jsonData = jsonData.rstrip()
    jsonData = jsonData.lstrip()

    jsonData = jsonData[:-1]

    basketballData = demjson.decode(jsonData)

    for playerData in basketballData:
        playerID = playerData['name']
        dateID = playerData['PMIN']


rotogrindersProjMin = playerData['PMIN']

file.write('%s, %s, %s')

INSERT
INTO
players_rotogrinders_proj_min
VALUES( % s, % s, % s)

file.close()

if __name__ == "__main__":
    rotogrinders_lastweek_scraper()
    rotogrinders_fourweeks_scraper()
    rotogrinders_season_scraper()

