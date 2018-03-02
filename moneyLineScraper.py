import mysql.connector as ms
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
import requests

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
        if single_date.day > 9:
            urls.append(
                'https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + str(
                    single_date.month) + str(single_date.day))
        else:
            urls.append(
                'https://www.sportsbookreview.com/betting-odds/nba-basketball/?date=' + str(single_date.year) + str(
                    single_date.month) + '0' + str(single_date.day))
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

    for url in urls:

        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        teams = soup.find_all('span', attrs={'class': 'team-name'})
        odds = soup.find_all('div', attrs={'class': 'eventLine-book-value'})

        for i in range(0, len(teams)//2):
            homeIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(homeIDStatement, (teams[i * 2].text,))
            homeID = cursor.fetchall()

            homeOdds = odds[i * 27 + 5].text.split()

            homeSpread = float(''.join(homeOdds[0][1:].replace("½",".5")))
            homeMoneyLine = float(''.join(homeOdds[1][1:].replace("½", ".5")))

            awayIDStatement = ("SELECT teamID FROM basketball.team_reference WHERE bovada = %s")
            cursor.execute(awayIDStatement, (teams[i * 2 + 1].text,))
            awayID = cursor.fetchall()

            awayOdds = odds[i * 27 + 6].text.split()

            awaySpread = float(''.join(awayOdds[0][1:].replace("½", ".5")))
            awayMoneyLine = float(''.join(awayOdds[1][1:].replace("½", ".5")))

            addGame = ("INSERT INTO game_odds (homeID, awayID, homeSpread, awaySpread, homeMoneyLine, awayMoneyLine) VALUES(%s, %s, %s, %s, %s, %s)")
            addGameD = (homeID[0][0], awayID[0][0], homeSpread, awaySpread, homeMoneyLine, awayMoneyLine)
            cursor.execute(addGame, addGameD)

        cnx.commit()

        print("Updated Historical Odds in game_odds for URL: " + str(url))

    cursor.close()
    cnx.commit()
    cnx.close()

if __name__ == "__main__":
    InsertGameOdds(constants.startDayP, constants.startMonthP, constants.startYearP,
                             constants.endDayP, constants.endMonthP, constants.endYearP)