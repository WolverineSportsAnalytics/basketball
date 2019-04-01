import mysql.connector
from datetime import timedelta, date
from bs4 import BeautifulSoup, Comment
import datetime as dt
import requests


def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP


# find the daterange to update
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def clean_tuple(inserts):
    inserts = list(inserts)

    return tuple(inserts)


def statsFiller(startDay, startMonth, startYear, endDay, endMonth, endYear, cnx, cursor):


    cursor = cnx.cursor(buffered=True)

    stmt = "Insert into basketball.team_performance (dailyTeamID, dailyTeamOpponentID, dateID, pointsAllowed, pointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, FTperFGA, offensiveRating, defensiveRating, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, offensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, win, loss, points1Q, points2Q, points3Q, points4Q) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    start_date_id = getDate(startDay, startMonth, startYear, cursor)
    end_date_id = getDate(endDay, endMonth, endYear, cursor)

    select_dates = "Select * from box_score_urls WHERE dateID >= %s AND dateID <= %s"
    boxScoreDatesD = (start_date_id, end_date_id)
    cursor.execute(select_dates, boxScoreDatesD)
    box_url = cursor.fetchall()

    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)

    url = []
    dates = []

    for single_date in daterange(start_date, end_date):
        dates.append(str(single_date.year) + '-' +
                     str(single_date.month) + '-' + str(single_date.day))
    date_counter = 0

    for urls in box_url:
        url = urls[1]
        dateID = urls[2]
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        # begin by determining the away team
        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))

        comment = comments[15]
        soup1 = BeautifulSoup(comment, "html.parser")
        for columns in soup1.find_all("tr")[2:3]:
            teamInfo = columns.find_all("a")
            opponentID = teamInfo[0].text

            selec_id = "select teamID from team_reference where bbreff=\""
            get_team = selec_id + opponentID + "\""
            cursor.execute(get_team)
            a_team_id = cursor.fetchall()[0][0]
            dailyTeamOpponentID = a_team_id

        for columns in soup1.find_all("tr")[3:4]:
            teamInfo = columns.find_all("a")
            non_opponentID = teamInfo[0].text

            selec_id = "select teamID from team_reference where bbreff=\""
            get_team = selec_id + non_opponentID + "\""
            cursor.execute(get_team)
            h_team_id = cursor.fetchall()[0][0]
            dailyTeamID = h_team_id

        # all this data is for the away team
        # first table box score with basic stats
        footersT1 = soup.find_all("tfoot")
        for footer in footersT1[:1]:
            table_data = footer.find_all("td")

            FG = int(table_data[1].text)
            FGA = int(table_data[2].text)
            FGP = float(table_data[3].text)
            threeP = int(table_data[4].text)
            threePA = int(table_data[5].text)
            threePP = float(table_data[6].text)
            FT = int(table_data[7].text)
            FTA = int(table_data[8].text)
            FTP = float(table_data[9].text)
            offensiveRebounds = int(table_data[10].text)
            defensiveRebounds = int(table_data[11].text)
            totalRebounds = int(table_data[12].text)
            assists = int(table_data[13].text)
            steals = int(table_data[14].text)
            blocks = int(table_data[15].text)
            turnovers = int(table_data[16].text)
            personalFouls = int(table_data[17].text)

        # second table box score with advanced stats
        footersT2 = soup.find_all("tfoot")
        for footer in footersT2[1:2]:
            table_data = footer.find_all("td")

            effectiveFieldGoalPercent = float(table_data[2].text)
            turnoverPercent = float(table_data[11].text)
            offensiveRating = float(table_data[13].text)
            defensiveRating = float(table_data[14].text)
            trueShootingPercent = float(table_data[1].text)
            threePointAttemptRate = float(table_data[3].text)
            freeThrowAttemptRate = float(table_data[4].text)
            defensiveReboundPercent = float(table_data[6].text)
            offensiveReboundPercent = float(table_data[5].text)
            totalReboundPercent = float(table_data[7].text)
            assistPercent = float(table_data[8].text)
            stealPercent = float(table_data[9].text)
            blockPercent = float(table_data[10].text)

        # retreives team name
        soup.findAll(text=lambda text: isinstance(text, Comment))

        comment = comments[16]
        box_score = comments[15]
        fourFactors = comments[16]

        soup2 = BeautifulSoup(box_score, "html.parser")
        box_scores = []
        for tr in soup2.find_all('tr')[2:]:
            for td in tr.find_all('td'):
                box_scores.append(td.text)

        # used to access the four factors table and line score table because values are stored in comments
        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        commentBox = comments[16]
        box_score = comments[15]

        # two data points that come from the fourFactors table
        soupFour = BeautifulSoup(fourFactors, "html.parser")
        pace = float(soupFour.find_all("td")[0].text)
        FTperFGA = float(soupFour.find_all("td")[4].text)

        # gets data in the scorebox
        for columns in soup1.find_all("tr")[2:3]:
            points1Q = int(columns.find_all("td")[1].text)
            points2Q = int(columns.find_all("td")[2].text)
            points3Q = int(columns.find_all("td")[3].text)
            points4Q = int(columns.find_all("td")[4].text)
            pointsScored = int(columns.find_all("td")[5].text)

        # gets opponent from scorebox
        for columns2 in soup1.find_all("tr")[3:4]:
            pointsAllowed = int(columns2.find_all("td")[5].text)

        if (pointsScored > pointsAllowed):
            win = 1
            loss = 0
        else:
            win = 0
            loss = 1

        team_insert_a_team = (
        dailyTeamID, dailyTeamOpponentID, dateID, pointsAllowed, pointsScored, pace, effectiveFieldGoalPercent,
        turnoverPercent, FTperFGA, offensiveRating, defensiveRating, FG, FGA, FGP, threeP, threePA, threePP, FT, FTA,
        FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls,
        trueShootingPercent, threePointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent,
        offensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, win, loss, points1Q,
        points2Q, points3Q, points4Q)

        team_insert_a_team = clean_tuple(team_insert_a_team)
        cursor.execute(stmt, team_insert_a_team)
        cnx.commit()

        # this is now the data for the home team
        for columns in soup1.find_all("tr")[3:4]:
            teamInfo = columns.find_all("a")
            opponentID = teamInfo[0].text

            selec_id = "select teamID from team_reference where bbreff=\""
            get_team = selec_id + opponentID + "\""
            cursor.execute(get_team)
            a_team_id = cursor.fetchall()[0][0]
            dailyTeamOpponentID = a_team_id

        for columns in soup1.find_all("tr")[2:3]:
            teamInfo = columns.find_all("a")
            non_opponentID = teamInfo[0].text

            selec_id = "select teamID from team_reference where bbreff=\""
            get_team = selec_id + non_opponentID + "\""
            cursor.execute(get_team)
            h_team_id = cursor.fetchall()[0][0]
            dailyTeamID = h_team_id

        # all this data is for the away team
        # first table box score with basic stats
        footersT1 = soup.find_all("tfoot")
        for footer in footersT1[2:3]:
            table_data = footer.find_all("td")

            FG = int(table_data[1].text)
            FGA = int(table_data[2].text)
            FGP = float(table_data[3].text)
            threeP = int(table_data[4].text)
            threePA = int(table_data[5].text)
            threePP = float(table_data[6].text)
            FT = int(table_data[7].text)
            FTA = int(table_data[8].text)
            FTP = float(table_data[9].text)
            offensiveRebounds = int(table_data[10].text)
            defensiveRebounds = int(table_data[11].text)
            totalRebounds = int(table_data[12].text)
            assists = int(table_data[13].text)
            steals = int(table_data[14].text)
            blocks = int(table_data[15].text)
            turnovers = int(table_data[16].text)
            personalFouls = int(table_data[17].text)

        # second table box score with advanced stats
        footersT2 = soup.find_all("tfoot")
        for footer in footersT2[3:4]:
            table_data = footer.find_all("td")

            effectiveFieldGoalPercent = float(table_data[2].text)
            turnoverPercent = float(table_data[11].text)
            offensiveRating = float(table_data[13].text)
            defensiveRating = float(table_data[14].text)
            trueShootingPercent = float(table_data[1].text)
            threePointAttemptRate = float(table_data[3].text)
            freeThrowAttemptRate = float(table_data[4].text)
            defensiveReboundPercent = float(table_data[6].text)
            offensiveReboundPercent = float(table_data[5].text)
            totalReboundPercent = float(table_data[7].text)
            assistPercent = float(table_data[8].text)
            stealPercent = float(table_data[9].text)
            blockPercent = float(table_data[10].text)

        # retreives team name
        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))

        comment = comments[16]
        box_score = comments[15]
        fourFactors = comments[16]

        soup2 = BeautifulSoup(box_score, "html.parser")
        box_scores = []
        for tr in soup2.find_all('tr')[2:]:
            for td in tr.find_all('td'):
                box_scores.append(td.text)

        # used to access the four factors table and line score table because values are stored in comments
        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        commentBox = comments[16]
        box_score = comments[15]

        # two data points that come from the fourFactors table
        soupFour = BeautifulSoup(fourFactors, "html.parser")
        pace = float(soupFour.find_all("td")[0].text)
        FTperFGA = float(soupFour.find_all("td")[4].text)

        # gets data in the scorebox
        for columns in soup1.find_all("tr")[3:4]:
            points1Q = int(columns.find_all("td")[1].text)
            points2Q = int(columns.find_all("td")[2].text)
            points3Q = int(columns.find_all("td")[3].text)
            points4Q = int(columns.find_all("td")[4].text)
            pointsScored = int(columns.find_all("td")[5].text)

        # gets opponent from scorebox
        for columns2 in soup1.find_all("tr")[2:3]:
            pointsAllowed = int(columns2.find_all("td")[5].text)

        if (pointsScored > pointsAllowed):
            win = 1
            loss = 0
        else:
            win = 0
            loss = 1

        team_insert_h_team = (
        dailyTeamID, dailyTeamOpponentID, dateID, pointsAllowed, pointsScored, pace, effectiveFieldGoalPercent,
        turnoverPercent, FTperFGA, offensiveRating, defensiveRating, FG, FGA, FGP, threeP, threePA, threePP, FT, FTA,
        FTP, offensiveRebounds, defensiveRebounds, totalRebounds, assists, steals, blocks, turnovers, personalFouls,
        trueShootingPercent, threePointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent,
        offensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, win, loss, points1Q,
        points2Q, points3Q, points4Q)

        team_insert_h_team = clean_tuple(team_insert_h_team)
        cursor.execute(stmt, team_insert_h_team)
        cnx.commit()

    return None

def auto(day, month, year, cnx, cursor):


    statsFiller(
            day, month, year, day, month, year, cnx, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()

def main():
    cursor.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    main()
()
