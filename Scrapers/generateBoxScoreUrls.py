"""
Steps:
1. Get the actual date
2. Convert the date to a dateID
3. Go to the basketball reference URL for that date
4. Get the list of games that are being played on that date
5. Get the URL for each of those games and insert each one into the database
"""

import mysql.connector
import constants
from bs4 import BeautifulSoup
import requests
from datetime import timedelta, date
import urllib2


# returns the dateID for a date in order to load data in for that dateID
def findDate(cursor, year, month, day):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
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
def generateBasketballReferenceURLs(cursor, year, month, day):
    cnx = mysql.connector.connect(user="root",
                                  host=127.0.0.1,
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    dateID = findDate(cursor, year, month, day)

    strMonth = ""
    if month == 10:
        strMonth = "october"
    elif month == 11:
        strMonth = "november"
    elif month == 12:
        strMonth = "december"
    elif month == 1:
        strMonth = "january"
    elif month == 2:
        strMonth = "february"
    elif month == 3:
        strMonth = "march"
    elif month == 4:
        strMonth = "april"

    page = requests.get("https://www.basketball-reference.com/leagues/NBA_20" + str(year) + "_games-" + str(strMonth) + ".html")
    soup = BeautifulSoup(page.text, 'html.parser')
    print(soup.find_all('th'))

    """
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
        boxScoreID = findDate(date.year, date.month, date.day, cursor)

        urlTuple = (newURL, boxScoreID)
        urls.append(urlTuple)
    except urllib2.HTTPError, e:
        badURLs.append(newURL)"""

def auto(day, month, year):
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    dates = generateDates(day, month, year,
                             day, month, year)


    generateBasketballReferenceURLs(cursor,dates)

    cursor.close()
    cnx.commit()
    cnx.close()

#function to generate all url's for one date

def URLSforDate(cursor, year, month, day):
    id = findDate(cursor, year, month, day)
    #need to get the number of games on that date - potential for loop
    #need to get the home team in abbreviated form to add to url
    
    page = requests.get("https://www.basketball-reference.com/leagues/NBA_20" + str(year) + "_games-" + str(strMonth) + str(day) + "0" + ".html")


#function to insert all these url's into table

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    #date = generateDates(constants.startDayP, constants.startMonthP, constants.startYearP,constants.endDayP, constants.endMonthP, constants.endYearP)

    generateBasketballReferenceURLs(cursor, constants.yearP, constants.monthP, constants.dayP)

    cursor.close()
    cnx.commit()
    cnx.close()
