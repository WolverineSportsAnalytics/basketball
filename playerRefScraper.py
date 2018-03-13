import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
import requests

"""
This scraper scrapes the player names and basketball reference IDs from the daily leaders URLs.
"""

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

# generates the urls for all daily leaders for each day
def generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urls = []
    for single_date in daterange(start_date, end_date):
        urls.append('https://www.basketball-reference.com/friv/dailyleaders.fcgi?month=' + str(single_date.month) +
                    '&day=' + str(single_date.day) + '&year=' + str(single_date.year))
    return urls

# insert references in sql to basketball reference, the player's name, and the player's team
def updateAndInsertPlayerRef(startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)

    cursor = cnx.cursor(buffered=True)

    for url in urls:

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        addPlayer = "INSERT INTO player_reference (nickName, bbrefID, firstName, lastName, team) VALUES(%s, %s, %s, %s, %s)"
        updatePlayer = "UPDATE player_reference SET team = %s WHERE bbrefID = %s"

        findPlayer = "SELECT bbrefID FROM player_reference WHERE bbrefID = %s"

        for tr in soup.find_all('tr')[1:]:
            # first find, then update

            try:
                tds = tr.find_all('td')
                nickName = tds[0].a.text
                lastName = tds[0]['csk'].split(",")[0]
                firstName = tds[0]['csk'].split(",")[1]
                bbref = tds[0]['data-append-csv']
                team = tds[1].a.text

                findPlayerQ = (bbref,)
                cursor.execute(findPlayer, findPlayerQ)

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

        print "Updated Basketball Players in Player Ref for URL: " + str(url)

    cursor.close()
    cnx.commit()
    cnx.close()

def auto():
    updateAndInsertPlayerRef(constants.startDayP, constants.startMonthP, constants.startYearP,
                             constants.endDayP, constants.endMonthP, constants.endYearP)


if __name__ == "__main__":
    updateAndInsertPlayerRef(constants.startDayP, constants.startMonthP, constants.startYearP,
                             constants.endDayP, constants.endMonthP, constants.endYearP)
