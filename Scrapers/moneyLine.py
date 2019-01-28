import mysql.connector as ms
from datetime import timedelta, date, datetime
import constants
from bs4 import BeautifulSoup
import urllib
import requests
import re
import json

"""
This file scrapes in spread and moneyline numbers from sportsbookreview for each game every day in any daterange.
"""

# function to iterate through a range of dates in the scrapers
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# function that generates all sportsbookreview urls within the daterange
def generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urls = []
    for single_date in daterange(start_date, end_date):
        if single_date.day > 9 and single_date.month > 9:
            urls.append(
                'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + str(single_date.year) + str(
                    single_date.month) + str(single_date.day))
        elif single_date.day > 9 and single_date.month < 10:
            urls.append(
                'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + str(single_date.year) + '0' +
                str(single_date.month) + str(single_date.day))
        elif single_date.day < 10 and single_date.month > 9:
            urls.append(
                'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + str(single_date.year) +
                str(single_date.month) + '0' + str(single_date.day))
        else:
            urls.append(
                'https://classic.sportsbookreview.com/betting-odds/nba-basketball/money-line/?date=' + str(single_date.year) + '0' +
                str(single_date.month) + '0' + str(single_date.day))
    return urls

# inserts the odds into sql
# inserts teamID, spread, moneyline
def InsertGameOdds(startDay, startMonth, startYear, endDay, endMonth, endYear):
    urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    cnx = ms.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)

    cursor = cnx.cursor(buffered=True)
    idOdds = 0

    for url in urls:

        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        teams = soup.find_all('span', attrs={'class': 'team-name'})
        odds = soup.find_all('div', attrs={'class': 'el-div eventLine-opener'})

        for i in range(0, len(teams)//2):
            # splits values from odds so numbers and other characters are separate
            gameOdds = odds[i].text
            print("Odds: ", gameOdds)

            homeIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(homeIDStatement, (teams[i * 2 + 1].text,))
            homeID = cursor.fetchall()

            awayIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(awayIDStatement, (teams[i * 2].text,))
            awayID = cursor.fetchall()

            if len(gameOdds) > 0:
                if gameOdds[0] == '+':
                    awayOdds = '+' + str(gameOdds[1:3])
                elif gameOdds[0] == '-':
                    awayOdds = '-' + str(gameOdds[1:3])
                if gameOdds[3] != '+' and gameOdds[3] != '-':
                    awayOdds += str(gameOdds[3])
                    if gameOdds[4] != '+' and gameOdds[4] != '-':
                        awayOdds += str(gameOdds[4])

                if gameOdds[3] == '+':
                    homeOdds = '+' + str(gameOdds[4:])
                elif gameOdds[3] == '-':
                    homeOdds = '-' + str(gameOdds[4:])
                elif gameOdds[4] == '+':
                    homeOdds = '+' + str(gameOdds[5:9])
                elif gameOdds[4] == '-':
                    homeOdds = '-' + str(gameOdds[5:9])
                elif gameOdds[5] == '+':
                    homeOdds = '+' + str(gameOdds[6:])
                elif gameOdds[5] == '-':
                    homeOdds = '-' + str(gameOdds[6:])
                elif gameOdds[6] == '+':
                    homeOdds = '+' + str(gameOdds[7:])
                elif gameOdds[6] == '-':
                    homeOdds = '-' + str(gameOdds[7:])
                elif gameOdds[2] == '+':
                    homeOdds = '+' + str(gameOdds[3:])
                elif gameOdds[2] == '-':
                    homeOdds = '-' + str(gameOdds[3:])

                print("Away odds: ", awayOdds)
                print("Home odds: ", homeOdds)

                '''homeSpread = float(''.join(homeOdds[0][1:].replace("½",".5")))

                awaySpread = float(''.join(awayOdds[0][1:].replace("½", ".5")))
                '''

                idOdds += 1
                print("Game number: ", idOdds)

                # add home and awaySpread later
                addGame = ("INSERT INTO game_odds (homeID, awayID, homeMoneyLine, awayMoneyLine) VALUES(%s, %s, %s, %s)")
                addGameD = (homeID[0][0], awayID[0][0], homeOdds[0:], awayOdds[0:])
                cursor.execute(addGame, addGameD)
                #insert home and away moneyline

                cnx.commit()

        print("Updated Historical Odds in game_odds for URL: " + str(url))

    cursor.close()
    cnx.commit()
    cnx.close()

def clear_table(cursor, cnx):
    ''' Helper Function to call in order to clear table after mistakes '''

    cursor.execute("Delete from game_odds")
    cursor.execute("ALTER TABLE game_odds AUTO_INCREMENT = 1")
    cnx.commit()

def my_split(s):
    return re.split(r'(\d+)', s)

if __name__ == "__main__":
    cnx = ms.connect(user="root",
                                  host='127.0.0.1',
                                  database="basketball",
                                  password="12345678")
    cursor = cnx.cursor(buffered=True)

    clear_table(cursor, cnx)

    now = datetime.today()
    
    InsertGameOdds(constants.startDayP, constants.startMonthP, constants.startYearP,
                             now.day, now.month, now.year)

    cursor.close()
    cnx.commit()
    cnx.close()
