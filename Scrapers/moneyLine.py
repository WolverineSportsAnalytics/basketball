# -*- coding: utf-8 -*-
import mysql.connector as ms
from datetime import timedelta, date, datetime
import constants
from bs4 import BeautifulSoup
import urllib
import requests

"""
This file scrapes in spread and moneyline numbers from sportsbookreview for each game every day in any daterange.
"""

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
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# function that generates all sportsbookreview urls within the daterange
def generateMoneyLineURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urlsToDate = {}
    urls = []
    for single_date in daterange(start_date, end_date):
        url = ""
        if single_date.day > 9 and single_date.month > 9:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + str(single_date.year) + str(
                    single_date.month) + str(single_date.day)
            urls.append(url)
        elif single_date.day > 9 and single_date.month < 10:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' +\
                  str(single_date.year) + '0' +str(single_date.month) + str(single_date.day)
            urls.append(url)
        elif single_date.day < 10 and single_date.month > 9:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + \
                  str(single_date.year) + str(single_date.month) + '0' + str(single_date.day)
            urls.append(url)
        else:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' +\
                  str(single_date.year) + '0' + str(single_date.month) + '0' + str(single_date.day)
            urls.append(url)
        urlsToDate[date(single_date.year, single_date.month, single_date.day)] = url
    return urlsToDate

def generateSpreadURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urlsToDate = {}
    urls = []
    for single_date in daterange(start_date, end_date):
        url = ""
        if single_date.day > 9 and single_date.month > 9:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year)\
                  + str(single_date.month) + str(single_date.day)
            urls.append(url)
        elif single_date.day > 9 and single_date.month < 10:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + '0'\
                  + str(single_date.month) + str(single_date.day)
            urls.append(url)
        elif single_date.day < 10 and single_date.month > 9:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + \
                  str(single_date.month) + '0' + str(single_date.day)
            urls.append(url)
        else:
            url = 'https://classic.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) +\
                  '0' + str(single_date.month) + '0' + str(single_date.day)
            urls.append(url)
        urlsToDate[date(single_date.year, single_date.month, single_date.day)] = url

    return urlsToDate

# inserts the odds into sql
# inserts teamID, moneyline
def InsertGameOdds(cursor, cnx, startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateMoneyLineURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)

    for date, url in urls.items():

        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        teams = soup.find_all('span', attrs={'class': 'team-name'})
        odds = soup.find_all('div', attrs={'class': 'el-div eventLine-opener'})

        dateID = findDate(cursor, date.year, date.month, date.day)

        for i in range(0, len(teams)//2):
            # splits values from odds so numbers and other characters are separate
            gameOdds = odds[i].text

            homeIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(homeIDStatement, (teams[i * 2 + 1].text,))
            homeID = cursor.fetchall()

            awayIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(awayIDStatement, (teams[i * 2].text,))
            awayID = cursor.fetchall()

            # separates home and away moneylines
            if len(gameOdds) > 0 and len(homeID) > 0 and len(awayID):
                if gameOdds[0] == '+':
                    awayOdds = '+' + str(gameOdds[1:3])
                elif gameOdds[0] == '-':
                    awayOdds = '-' + str(gameOdds[1:3])
                if gameOdds[3] != '+' and gameOdds[3] != '-':
                    awayOdds += str(gameOdds[3])
                    if len(gameOdds) > 4:
                        if gameOdds[4] != '+' and gameOdds[4] != '-':
                            awayOdds += str(gameOdds[4])

                homeOdds = None
                if len(gameOdds) > 3:
                    if gameOdds[3] == '+':
                        homeOdds = '+' + str(gameOdds[4:])
                    elif gameOdds[3] == '-':
                        homeOdds = '-' + str(gameOdds[4:])
                    if len(gameOdds) > 4:
                        if gameOdds[4] == '+':
                            homeOdds = '+' + str(gameOdds[5:9])
                        elif gameOdds[4] == '-':
                            homeOdds = '-' + str(gameOdds[5:9])
                        if len(gameOdds) > 5:
                            if gameOdds[5] == '+':
                                homeOdds = '+' + str(gameOdds[6:])
                            elif gameOdds[5] == '-':
                                homeOdds = '-' + str(gameOdds[6:])
                            if len(gameOdds) > 6:
                                if gameOdds[6] == '+':
                                    homeOdds = '+' + str(gameOdds[7:])
                                elif gameOdds[6] == '-':
                                    homeOdds = '-' + str(gameOdds[7:])
                else:
                    if len(gameOdds) > 2:
                        if gameOdds[2] == '+':
                            homeOdds = '+' + str(gameOdds[3:])
                        elif gameOdds[2] == '-':
                            homeOdds = '-' + str(gameOdds[3:])

                addGame = ("INSERT INTO game_odds (homeID, awayID, homeMoneyLine, awayMoneyLine, dateID) VALUES(%s, %s, %s, %s, %s)")
                addGameD = (homeID[0][0], awayID[0][0], homeOdds[0:], awayOdds[0:], dateID)
                cursor.execute(addGame, addGameD)

                cnx.commit()

        print("Updated Historical Odds in game_odds for URL: " + str(url))

    cnx.commit()

def InsertGameSpread(cursor, cnx, startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateSpreadURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)

    id = 0

    for date, url in urls.items():

        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        teams = soup.find_all('span', attrs={'class': 'team-name'})
        spread = soup.find_all('div', attrs={'class': 'el-div eventLine-opener'})

        dateID = findDate(cursor, date.year, date.month, date.day)

        for i in range(0, len(teams)//2):

            gameSpread = spread[i].text

            homeIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(homeIDStatement, (teams[i * 2 + 1].text,))
            homeID = cursor.fetchall()

            awayIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(awayIDStatement, (teams[i * 2].text,))
            awayID = cursor.fetchall()

            # separates home and away moneylines
            if len(gameSpread) > 0 and len(homeID) > 0 and len(awayID):
                # home and away spreads are same numbers just opposite signs
                if gameSpread[3] != '+' and gameSpread[3] != '-' and gameSpread[0] != 'P':

                    if gameSpread[0] == '+':
                        awaySpread = '+' + gameSpread[1:4]
                        homeSpread = '-' + gameSpread[1:4]
                    if gameSpread[0] == '-':
                        awaySpread = '-' + gameSpread[1:4]
                        homeSpread = '+' + gameSpread[1:4]

                elif gameSpread[3] == '+' or gameSpread[3] == '-' and gameSpread[0] != 'P':

                    if gameSpread[0] == '+':
                        awaySpread = '+' + gameSpread[1:3]
                        homeSpread = '-' + gameSpread[1:3]
                    elif gameSpread[0] == '-':
                        awaySpread = '-' + gameSpread[1:3]
                        homeSpread = '+' + gameSpread[1:3]

                # PK means pick 'em so even money wagers
                if gameSpread[0] == 'P' and gameSpread[1] == 'K':
                    awaySpread = "0"
                    homeSpread = "0"

                # replaces ½ with .5 in both home and away spreads
                if gameSpread[0] != 'P':
                    if awaySpread[1] == "½":
                        awaySpread = awaySpread[0] + awaySpread[1].replace("½", ".5")
                        homeSpread = homeSpread[0] + awaySpread[1:]
                    elif awaySpread[2] == "½":
                        awaySpread = awaySpread[0:2] + awaySpread[2].replace("½", ".5")
                        homeSpread = homeSpread[0] + awaySpread[1:]

                    if len(awaySpread) > 3:
                        if awaySpread[3] == "½" and awaySpread[0] != 'P':
                            awaySpread = awaySpread[0:3] + awaySpread[3].replace("½", ".5")
                            homeSpread = homeSpread[0] + awaySpread[1:]

                id += 1

                # add home and awaySpread by updating table
                addGame = ("UPDATE game_odds SET homeSpread=%s, awaySpread=%s WHERE dateID=%s AND awayID=%s AND homeID=%s")
                addGameD = (float(homeSpread[0:]), float(awaySpread[0:]), dateID, awayID[0][0], homeID[0][0])
                cursor.execute(addGame, addGameD)

                cnx.commit()

        print("Updated Historical Odds in game_odds for URL: " + str(url))

    cnx.commit()

def clear_table(cursor, cnx):
    ''' Helper Function to call in order to clear table after mistakes '''

    cursor.execute("Delete from game_odds")
    cursor.execute("ALTER TABLE game_odds AUTO_INCREMENT = 1")
    cnx.commit()

if __name__ == "__main__":
    cnx = ms.connect(user="wsa",
                                  host='34.68.250.121',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)

    #clear_table(cursor, cnx)

    now = datetime.today()

    InsertGameOdds(cursor, cnx, constants.startDayP, constants.startMonthP, constants.startYearP, constants.endDayP, constants.endMonthP, constants.endYearP)
    InsertGameSpread(cursor, cnx, constants.startDayP, constants.startMonthP, constants.startYearP, constants.endDayP, constants.endMonthP, constants.endYearP)

    cursor.close()
    cnx.commit()
    cnx.close()
