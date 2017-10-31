import re
import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def updateAndInsertPlayerRef(
        startDay,
        startMonth,
        startYear,
        endDay,
        endMonth,
        endYear,
        cursor):

    # set range of dates
    #urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)

    insert_team_data = "INSERT INTO basketball.team_performance (dailyTeamID, dailyTeamOpponentID, dateID, pointsAllowed, pointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, FTperFGA, offensiveRating, defensiveRating, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, offensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, win, loss, points1Q, points2Q, points3Q, points4Q) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    select_dates = "Select * from box_score_urls;"
    cursor.execute(select_dates)
    box_url = cursor.fetchall()
    url = []

    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)

    dates = []
    for single_date in daterange(start_date, end_date):
        dates.append(str(single_date.year) + '-' +
                     str(single_date.month) + '-' + str(single_date.day))

    date_counter = 0

    # loop through all url's
    for urls in box_url:
        url = urls[1]
        date_id = urls[2]
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        comment = comments[len(comments) - 23]
        box_score = comments[len(comments) - 24]

        soup2 = BeautifulSoup(box_score, "html.parser")
        box_scores = []
        for tr in soup2.find_all('tr')[2:]:
            for td in tr.find_all('td'):

                box_scores.append(td.text)

        teams_data = [[], []]
        soup1 = BeautifulSoup(comment, "html.parser")
        team_num = 0

        for tr in soup1.find_all('tr')[2:]:

                # team name
            team = tr.find_all('th')[0].text

            # table columns

            tds = tr.find_all('td')
            pace = tds[0].text
            eShooting = tds[1].text
            turnoverPercent = tds[2].text
            oReboundPercent = tds[3].text
            FTOverFQAttempts = tds[4].text
            ORTG = tds[5].text

            teams_data[team_num].append(team)
            teams_data[team_num].append(pace)
            teams_data[team_num].append(eShooting)
            teams_data[team_num].append(turnoverPercent)
            teams_data[team_num].append(oReboundPercent)
            teams_data[team_num].append(FTOverFQAttempts)
            teams_data[team_num].append(ORTG)
            team_num = +1

        team_num = 0
        for tfoot in soup.find_all('tfoot'):
            td = tfoot.find_all('td')
            for i in td:
                teams_data[team_num / 2].append(i.text)
            team_num += 1

        teams_data[0].append(teams_data[1][0])
        teams_data[1].append(teams_data[0][0])

        selec_id = "select teamID from team_reference where bbreff=\""
        get_team = selec_id + teams_data[0][0] + "\""
        cursor.execute(get_team)
        h_team_id = cursor.fetchall()[0][0]

        get_team = selec_id + teams_data[1][0] + "\""
        cursor.execute(get_team)
        a_team_id = cursor.fetchall()[0][0]

        teams_data[0][0] = h_team_id
        teams_data[0][len(teams_data[0]) - 1] = a_team_id
        teams_data[1][0] = a_team_id
        teams_data[1][len(teams_data[0]) - 1] = h_team_id

        teams_data[1].append(teams_data[0][25])
        teams_data[0].append(teams_data[1][25])

        times = 0
        for team in teams_data:
            if times == 0:
                q1 = box_scores[1]
                q2 = box_scores[2]
                q3 = box_scores[3]
                q4 = box_scores[4]
                score = box_scores[5]
                opp_score = box_scores[11]
                if score > opp_score:
                    win = 1
                    loss = 0
                else:
                    win = 0
                    loss = 1
            else:
                q1 = box_scores[7]
                q2 = box_scores[8]
                q3 = box_scores[9]
                q4 = box_scores[10]
                score = box_scores[11]
                opp_score = box_scores[5]
                if score > opp_score:
                    win = 1
                    loss = 0
                else:
                    win = 0
                    loss = 1

            team_insert = (team[0],
                           team[len(team) - 2],
                           (date_id),
                           team[len(team) - 1],
                           team[25],
                           team[1],
                           team[2],
                           team[3],
                           team[5],
                           team[6],
                           team[41],
                           team[8],
                           team[9],
                           team[10],
                           team[11],
                           team[12],
                           team[13],
                           team[14],
                           team[15],
                           team[16],
                           team[17],
                           team[18],
                           team[19],
                           team[20],
                           team[21],
                           team[22],
                           team[23],
                           team[24],
                           team[28],
                           team[30],
                           team[31],
                           team[33],
                           team[32],
                           team[34],
                           team[35],
                           team[36],
                           team[37],
                           win,
                           loss,
                           q1,
                           q2,
                           q3,
                           q4
                           )

            cursor.execute(insert_team_data, team_insert)
            cnx.commit()
            times += 1


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    updateAndInsertPlayerRef(
        constants.startDayP,
        constants.startMonthP,
        constants.startYearP,
        constants.endDayP,
        constants.endMonthP,
        constants.endYearP,
        cursor)

    cursor.close()
    cnx.commit()
    cnx.close()
