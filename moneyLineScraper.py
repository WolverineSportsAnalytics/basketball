import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
import urllib2
import requests

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urls = []
    for single_date in daterange(start_date, end_date):
        urls.append('https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year)) + str(single_date.month) + str(single_date.day))
    return urls

#https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=20171011

def InsertGameOdds(startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)

    cursor = cnx.cursor(buffered=True)

    for url in urls:

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        addGame = "INSERT INTO game_odds (homeID, awayID, homeSpread, awaySpread, homeMoneyLine, awayMoneyLine) VALUES(%s, %s, %s, %s, %s, %s)"

        for tr in soup.find_all("div", { "class" : "status" })[1:]:
            # first find, then update

            try:
                tds = tr.find_all('')       #FIX THIS STUFF
                nickName = tds[0].a.text
                lastName = tds[0]['csk'].split(",")[0]
                firstName = tds[0]['csk'].split(",")[1]
                bbref = tds[0]['data-append-csv']
                team = tds[1].a.text

                if cursor.rowcount == 0:
                    # add because did not find anything
                    names = (nickName, bbref, firstName, lastName, team)
                    cursor.execute(addPlayer, names)
                else:
                    # update
                    updatePQ = (team, bbref)
                    cursor.execute(updatePlayer, updatePQ)
            except:
                pass

        cnx.commit()

        print "Updated Historical Odds in game_odds for URL: " + str(url)

    cursor.close()
    cnx.commit()
    cnx.close()

if __name__ == "__main__":
    updateAndInsertPlayerRef(constants.startDayP, constants.startMonthP, constants.startYearP,
                             constants.endDayP, constants.endMonthP, constants.endYearP)