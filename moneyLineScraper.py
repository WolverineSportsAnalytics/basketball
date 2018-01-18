import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
import urllib
import requests

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urls = []
    for single_date in daterange(start_date, end_date):
        if single_date.day > 9:
            urls.append(
                'https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + str(
                    single_date.month) + str(single_date.day))
        else:
            urls.append(
                'https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + str(
                    single_date.month) + '0' + str(single_date.day))
    return urls

def InsertGameOdds(startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)

    cursor = cnx.cursor(buffered=True)

    for url in urls:

        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        #addGame = "INSERT INTO game_odds (homeID, awayID, homeSpread, awaySpread, homeMoneyLine, awayMoneyLine) VALUES(%s, %s, %s, %s, %s, %s)"
        addTeamID = "INSERT INTO game_odds (homeID, awayID) VALUES(%s, %s)"

        for team in soup.find_all('span', attrs={'class': 'team-name'})[:]:
            # first find, then update
            print(team.text)l


        for odds in soup.find_all('div', attrs={'class': 'eventLine-book-value'})[:]:
            print(odds.text)

            """
            try:
                allDivs = game.find_all("div")[1:]       #FIX THIS STUFF
                print(allDivs[0].text)
                #names = (homeID, awayID, homeSpread, awaySpread, homeMoneyLine, awayMoneyLine)
                #cursor.execute(addGame, names)

            except:
                pass"""

        cnx.commit()

        print("Updated Historical Odds in game_odds for URL: " + str(url))

    cursor.close()
    cnx.commit()
    cnx.close()

if __name__ == "__main__":
    InsertGameOdds(constants.startDayP, constants.startMonthP, constants.startYearP,
                             constants.endDayP, constants.endMonthP, constants.endYearP)