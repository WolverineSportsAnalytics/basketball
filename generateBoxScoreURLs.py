import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
import urllib2
import requests


# returns the dateID for a date in order to load data in for that dateID
def findDate(year, month, day):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# Generates dates from a range and loads them into the new_dates table in sql to create dateIDs
def generateDates(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    dates = []
    for single_date in daterange(start_date, end_date):
        dates.append(single_date)
    return dates

# returns an array of all NBA teams
def getTeams(cursor):
    teamQuery = "SELECT bbreff FROM team_reference"
    cursor.execute(teamQuery)

    teams = []
    for team in cursor:
        teams.append(team[0])

    return teams

# function that generates all valid basketball reference urls
def generateBasketballReferenceURLs(cursor):
    #year month day 0 team
    # if pipe is broken, must delete all the values from the first day, then restart the boxscore url from
    # that day that was just deleted
    dates = generateDates(constants.startDayP, constants.startMonthP, constants.startYearP,
                  constants.endDayP, constants.endMonthP, constants.endYearP)

    teams = getTeams(cursor)

    urls = []
    badURLs = []
    baseURL = constants.BasketballRefBoxScoreBase

    for date in dates:
        for team in teams:
            shouldSave = len(urls) % 1
            if shouldSave == 0 and len(urls) != 0:
                queryBoxScoreURL = "INSERT INTO box_score_urls (url, dateID) VALUES (%s, %s)"
                cursor.executemany(queryBoxScoreURL, urls)
                cnx.commit()
                print "Inserted + Committed URLs"
                urls = []

            month = ""
            day = ""

            if len(str(date.month)) == 1:
                month = "0" + str(date.month)
            else:
                month = str(date.month)

            if len(str(date.day)) == 1:
                day = "0" + str(date.day)
            else:
                day = str(date.day)

            newURL = baseURL + str(date.year) + month + day + str(0) + team + ".html"
            try:
                urllib2.urlopen(newURL)
                boxScoreID = findDate(date.year, date.month, date.day)

                urlTuple = (newURL, boxScoreID)
                urls.append(urlTuple)
            except urllib2.HTTPError, e:
                badURLs.append(newURL)

def auto():
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    generateBasketballReferenceURLs(cursor)

    cursor.close()
    cnx.commit()
    cnx.close()



if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    generateBasketballReferenceURLs(cursor)

    cursor.close()
    cnx.commit()
    cnx.close()

