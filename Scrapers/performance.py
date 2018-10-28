import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import requests
import datetime as dt

def getDate(day, month, year, cursor):
    # set query parameters
    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)

    # query database and get id for given date
    cursor.execute(findGame, findGameData)

    # return result
    return cursor.fetchone()[1]

def daterange(start_date, end_date):
    # return list of dates between start_date and end_date using
    # generator to save memory usage
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def updateAndInsertPlayerRef(
        startDay,
        startMonth,
        startYear,
        endDay,
        endMonth,
        endYear,
        cursor,
        cnx):

    # set range of dates
    # urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)

    # get start_date_id and print it

    start_date_id = getDate(startDay, startMonth, startYear, cursor)
    print start_date_id

    # get end_date_id and print it

    end_date_id = getDate(endDay, endMonth, endYear, cursor)
    print end_date_id

    # query database and get all box_score_urls with dateID between start_date_id and end_date_id

    select_dates = "Select * from box_score_urls WHERE dateID >= %s AND dateID <= %s"
    boxScoreDatesD = (start_date_id, end_date_id)
    cursor.execute(select_dates, boxScoreDatesD)

    # store result of query in box_url

    box_url = cursor.fetchall()

    selec_id_id = "select playerID from player_reference where bbrefID= %s"
    selec_id = "select playerID from player_reference where nickName=\""

    # loop through all url's
    for score in box_url:

        url = score[1]

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        soup.findAll(text=lambda text: isinstance(text, Comment))
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))

        comment = comments[len(comments) - 24]
        soup1 = BeautifulSoup(comment, "html.parser")

        teams = []
        for i in soup1.find_all('tr')[2:]:
            l = i.find_all("td")[0].text
            teams.append(l)
        date_id = score[2]

        tables = soup.find_all("tbody")

        team_tables = [[tables[0], tables[1], teams[0], teams[1], 0], [
            tables[2], tables[3], teams[1], teams[0], 1]]

        for team in team_tables:
            # set team specific data
            tea = team[2]
            opp = team[3]
            rows_1 = team[0].find_all('tr')
            rows_2 = team[1].find_all('tr')
            home = team[4]
            # scrape regular stats
            for number in range(len(rows_1)):
                # first find, then updated
                    try:
                        bbrefID = rows_1[number].find_all('th')[0]['data-append-csv']
                        bbrefData = (bbrefID,)
                        cursor.execute(selec_id_id, bbrefData)
                        player_id = cursor.fetchall()[0][0]
                    except:
                        pass

                    try:
                        nickName = rows_1[number].find_all('th')[0].a.text
                        tds1 = rows_1[number].find_all('td')
                        get_id = selec_id + nickName + "\""
                        cursor.execute(get_id)
                        player_id = cursor.fetchall()[0][0]
                    except:
                        pass


                    try:
                        if tds1[0].text == "Did Not Play":
                            minutes = 0
                            blocks = 0
                            steals = 0
                            points = 0
                            assists = 0
                            to = 0
                            rebounds = 0
                            triple_double = 0
                            double_double = 0
                            o_rebs = 0
                            d_rebs = 0
                            fgs = 0
                            fga = 0
                            fgpercent = 0
                            tpm = 0
                            tpa = 0
                            tp_percent = 0
                            free_throws = 0
                            fta = 0
                            ft_percent = 0
                            pf = 0
                            plus_minus = 0
                            TS = 0
                            eFG = 0
                            TPAR = 0
                            FTR = 0
                            ORBR = 0
                            DRBR = 0
                            TRBR = 0
                            ASTR = 0
                            STLR = 0
                            BLKR = 0
                            TOVR = 0
                            USGR = 0
                            ORtg = 0
                            DRtg = 0
                        else:
                            minutes = tds1[0].text

                            blocks = tds1[15].text
                            steals = tds1[14].text
                            points = tds1[18].text
                            assists = tds1[13].text
                            to = tds1[16].text
                            rebounds = tds1[12].text
                            triple_double = 0
                            double_double = 0
                            o_rebs = tds1[10].text
                            d_rebs = tds1[11].text

                            fgs = tds1[1].text
                            fga = tds1[2].text
                            if fga == 0:
                                fgpercent = "NULL"
                            else:
                                fgpercent = tds1[3].text

                            tpm = tds1[4].text
                            tpa = tds1[5].text
                            if tpa == 0:
                                tp_percent = "NULL"
                            else:
                                tp_percent = tds1[6].text

                            free_throws = tds1[7].text
                            fta = tds1[8].text
                            if fta == 0:
                                ft_percent = "NULL"
                            else:
                                ft_percent = tds1[9].text

                            pf = tds1[17].text

                            #plus_minus = tds1[19].text
                            plus_minus = '0'

                            # advanced statistics
                            tds = rows_2[number].find_all('td')
                            TS = tds[1].text
                            eFG = tds[2].text
                            TPAR = tds[3].text
                            FTR = tds[4].text
                            ORBR = tds[5].text
                            DRBR = tds[6].text
                            TRBR = tds[7].text
                            ASTR = tds[8].text
                            STLR = tds[9].text
                            BLKR = tds[10].text
                            TOVR = tds[11].text
                            USGR = tds[12].text
                            ORtg = tds[13].text
                            DRtg = tds[14].text

                            plus_tens = 0
                            if int(steals) >= 10:
                                plus_tens += 1
                            if int(blocks) >= 10:
                                plus_tens += 1
                            if int(points) >= 10:
                                plus_tens += 1
                            if int(assists) >= 10:
                                plus_tens += 1
                            if int(rebounds) >= 10:
                                plus_tens += 1

                            if plus_tens > 2:
                                triple_double = 1
                            elif plus_tens > 1:
                                double_double = 1

                        inserts = (
                            player_id,
                            date_id,
                            points,
                            minutes,
                            fgs,
                            fga,
                            fgpercent,
                            tpm,
                            tpa,
                            tp_percent,
                            free_throws,
                            fta,
                            ft_percent,
                            o_rebs,
                            d_rebs,
                            rebounds,
                            assists,
                            steals,
                            blocks,
                            to,
                            pf,
                            plus_minus,
                            TS,
                            eFG,
                            TPAR,
                            FTR,
                            ORBR,
                            DRBR,
                            TRBR,
                            ASTR,
                            STLR,
                            BLKR,
                            TOVR,
                            USGR,
                            ORtg,
                            DRtg,
                            triple_double,
                            double_double,
                            tea,
                            opp,
                            home)
                        new_insert = (
                            points,
                            minutes,
                            fgs,
                            fga,
                            fgpercent,
                            tpm,
                            tpa,
                            tp_percent,
                            free_throws,
                            fta,
                            ft_percent,
                            o_rebs,
                            d_rebs,
                            rebounds,
                            assists,
                            steals,
                            blocks,
                            to,
                            pf,
                            plus_minus,
                            TS,
                            eFG,
                            TPAR,
                            FTR,
                            ORBR,
                            DRBR,
                            TRBR,
                            ASTR,
                            STLR,
                            BLKR,
                            TOVR,
                            USGR,
                            ORtg,
                            DRtg,
                            triple_double,
                            double_double,
                            tea,
                            opp,
                            home,
                            player_id,
                            date_id

                            )
                        update_performance = "INSERT INTO performance (playerID, dateID, points, minutesPlayed, fieldGoals, fieldGoalsAttempted, fieldGoalPercent, 3PM, 3PA, 3PPercent, FT, FTA, FTPercent, offensiveRebounds, defensiveRebounds, totalRebounds, assists,  steals, blocks, turnovers, personalFouls, plusMinus, trueShootingPercent, effectiveFieldGoalPercent, 3pointAttemptRate, freeThrowAttemptRate, offensiveReboundPercent, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, turnoverPercent, usagePercent, offensiveRating, defensiveRating,  tripleDouble, doubleDouble, team, opponent, home) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        true_update_perf = "UPDATE performance set points=%s, minutesPlayed=%s, fieldGoals=%s, fieldGoalsAttempted=%s, fieldGoalPercent=%s, 3PM=%s, 3PA=%s, 3PPercent=%s, FT=%s, FTA=%s, FTPercent=%s, offensiveRebounds=%s, defensiveRebounds=%s, totalRebounds=%s, assists=%s,  steals=%s, blocks=%s, turnovers=%s, personalFouls=%s, plusMinus=%s, trueShootingPercent=%s, effectiveFieldGoalPercent=%s, 3pointAttemptRate=%s, freeThrowAttemptRate=%s, offensiveReboundPercent=%s, defensiveReboundPercent=%s, totalReboundPercent=%s, assistPercent=%s, stealPercent=%s, blockPercent=%s, turnoverPercent=%s, usagePercent=%s, offensiveRating=%s, defensiveRating=%s,  tripleDouble=%s, doubleDouble=%s, team=%s, opponent=%s, home=%s where playerID= %s and dateID = %s"

                        check = "SELECT * from performance where dateID = %s and playerID = %s"
                        cursor.execute(check,(date_id,player_id))
                        checks = cursor.fetchall()
                        if len(checks) > 0:
                            print "updates"
                            print new_insert
                            cursor.execute(true_update_perf, new_insert)
                            cnx.commit()
                            print true_update_perf
                            print new_insert


                        else:
                            cursor.execute(update_performance, inserts)

                        cnx.commit()
                    except:
                        pass

    cleanUp = "DELETE FROM performance WHERE blocks IS NULL"
    cursor.execute(cleanUp)

if __name__ == "__main__":

    # initiate connection with database
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    # call function to insert data into performance table
    updateAndInsertPlayerRef(
        constants.startDayP,
        constants.startMonthP,
        constants.startYearP,
        constants.endDayP,
        constants.endMonthP,
        constants.endYearP,
        cursor,
        cnx)

    # close connection with database
    cursor.close()
    cnx.commit()
    cnx.close()