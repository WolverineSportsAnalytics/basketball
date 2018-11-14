import mysql.connector
from bs4 import BeautifulSoup, Comment
import requests
import datetime as dt
import numpy as np

# get dateID of given date
def getDate(day, month, year, cursor):
    # set query parameters
    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)

    # query database and get id for given date
    cursor.execute(findGame, findGameData)

    # return result
    return cursor.fetchone()[0]

# get boxscoreurls of games in date range
def getURLs(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor):
    # get start_date_id
    start_date_id = getDate(startDay, startMonth, startYear, cursor)

    # get end_date_id
    end_date_id = getDate(endDay, endMonth, endYear, cursor)

    # query database and get all box_score_urls with dateID between start_date_id and end_date_id
    select_dates = "Select * from box_score_urls WHERE dateID >= %s AND dateID <= %s"

    boxScoreDatesD = (start_date_id, end_date_id)

    cursor.execute(select_dates, boxScoreDatesD)

    # return result of query
    return cursor.fetchall()

# get playerID given bbrefID
def getPlayerID(bbrefID, cursor):
    # set query parameters
    selec_player_id = "select playerID from player_reference where bbrefID= %s"

    # query database and get playerID
    bbrefData = (bbrefID,)
    cursor.execute(selec_player_id, bbrefData)

    # return result of query
    return cursor.fetchone()[0]

# remove row of data from performance table where the blocks are empty
def cleanup(cursor, cnx):

    cleanUp = "DELETE FROM performance WHERE blocks IS NULL"

    # delete from database
    cursor.execute(cleanUp)
    cnx.commit()

# insert perfomance data into database
def insertperformance(basictable, advancedtable, team, opp, homeaway, date_id, cursor, cnx):

    # table 1 row 1
    basic = basictable[0].find_all('tr')

    # table 2 row 1
    advance = advancedtable[0].find_all('tr')

    # scrape regular stats
    for number in range(len(basic)):

        # skip the sixth row in the table since it is a sub-header row
        if (number == 5):
            continue

        # get basketball reference ID from html script
        bbrefID = basic[number].find_all('th')[0]['data-append-csv']

        # use bbrefID to get player_id through database
        player_id = getPlayerID(bbrefID, cursor)

        # get all table cells of basic table
        tdbasic = basic[number].find_all('td')

        # check if the player played the game
        if tdbasic[0].text == "Did Not Play" or tdbasic[0].text == "Not With Team" or tdbasic[0].text == "Did Not Dress":
            # set all stats equal to 0
            continue

        else:
            # record each respective basic stats
            minutes_raw = str(tdbasic[0].text).split(':')
            minutes = int(minutes_raw[0]) + float(minutes_raw[1]) / 60.0
            fgs = tdbasic[1].text
            fga = tdbasic[2].text

            if int(fga) == 0:
                fgpercent = 0
            else:
                fgpercent = tdbasic[3].text

            tpm = tdbasic[4].text
            tpa = tdbasic[5].text

            if int(tpa) == 0:
                tp_percent = 0
            else:
                tp_percent = tdbasic[6].text

            free_throws = tdbasic[7].text
            fta = tdbasic[8].text

            if int(fta) == 0:
                ft_percent = 0
            else:
                ft_percent = tdbasic[9].text

            o_rebs = tdbasic[10].text
            d_rebs = tdbasic[11].text
            rebounds = tdbasic[12].text
            assists = tdbasic[13].text
            steals = tdbasic[14].text
            blocks = tdbasic[15].text
            to = tdbasic[16].text
            pf = tdbasic[17].text
            points = tdbasic[18].text

            triple_double = 0
            double_double = 0

            plus_minus_raw = str(tdbasic[19].text)
            if plus_minus_raw == '' or plus_minus_raw == '0':
                plus_minus = 0
            elif plus_minus_raw.find('-'):
                plus_minus = -int(plus_minus_raw[1:])
            else:
                plus_minus = int(plus_minus_raw[1:])

            # record each respective advanced stats
            tdadvance = advance[number].find_all('td')

            TS = tdadvance[1].text
            if TS == '':
                TS = 0
            eFG = tdadvance[2].text
            if eFG == '':
                eFG = 0
            TPAR = tdadvance[3].text
            if TPAR == '':
                TPAR = 0
            FTR = tdadvance[4].text
            if FTR == '':
                FTR = 0
            ORBR = tdadvance[5].text
            if ORBR == '':
                ORBR = 0
            DRBR = tdadvance[6].text
            if DRBR == '':
                DRBR = 0
            TRBR = tdadvance[7].text
            if TRBR == '':
                TRBR = 0
            ASTR = tdadvance[8].text
            if ASTR == '':
                ASTR = 0
            STLR = tdadvance[9].text
            if STLR == '':
                STLR = 0
            BLKR = tdadvance[10].text
            if BLKR == '':
                BLKR = 0
            TOVR = tdadvance[11].text
            if TOVR == '':
                TOVR = 0
            USGR = tdadvance[12].text
            if USGR == '':
                USGR = 0
            ORtg = tdadvance[13].text
            if ORtg == '':
                ORtg = 0
            DRtg = tdadvance[14].text
            if DRtg == '':
                DRtg = 0

            # caculate double doubles and triple doubles
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

            # make array of all stats
            inserts = (player_id, date_id, points, minutes, fgs,
                       fga, fgpercent, tpm, tpa, tp_percent,
                       free_throws, fta, ft_percent, o_rebs, d_rebs,
                       rebounds, assists, steals, blocks, to,
                       pf, plus_minus, TS, eFG, TPAR,
                       FTR, ORBR, DRBR, TRBR, ASTR,
                       STLR, BLKR, TOVR, USGR, ORtg,
                       DRtg, triple_double, double_double, team, opp,
                       homeaway)

        # set up insert statement of database
        insert_performance = "INSERT INTO performance (playerID, dateID, points, minutesPlayed, fieldGoals, fieldGoalsAttempted, fieldGoalPercent, 3PM, 3PA, 3PPercent, FT, FTA, FTPercent, offensiveRebounds, defensiveRebounds, totalRebounds, assists,  steals, blocks, turnovers, personalFouls, plusMinus, trueShootingPercent, effectiveFieldGoalPercent, 3pointAttemptRate, freeThrowAttemptRate, offensiveReboundPercent, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, turnoverPercent, usagePercent, offensiveRating, defensiveRating,  tripleDouble, doubleDouble, team, opponent, home) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # insert performance data to database
        cursor.execute(insert_performance, inserts)
        cnx.commit()

# get team names from url
def getTeams(url):
    teams = []

    # get source code from url
    page = requests.get(url)

    # create beautiful soup using html text
    soup = BeautifulSoup(page.text, 'html.parser')

    comments = soup.findAll(text=lambda text: isinstance(text, Comment))

    # find div tag with class "game_summary nohover current"
    soup1 = BeautifulSoup(comments[11], 'html.parser')
    div = soup1.find_all("div",'game_summary nohover current')

    # find tr in div
    for tr in div[0].find_all('tr'):
        # find team names in tr
        name = tr.find_all('td')[0].text

        teams.append(name)

    # return teams (away, home)
    return teams

# get tables from url
def getTables(url):
    tables = []

    # get source code from url
    page = requests.get(url)

    # create beautiful soup using html text
    soup = BeautifulSoup(page.text, 'html.parser')

    # find table tag with class "sortable stats_table"
    for table in soup.find_all("table", 'sortable stats_table'):
        # find tbody in table
        tbody = table.find_all('tbody')

        tables.append(tbody)

    # return tables (basic away, advanced away, basic home, advanced home)
    return tables

# insert performance in given date
def updateAndInsertPlayerRef(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor, cnx):

    # get boxurls in given range of dates
    box_url = getURLs(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor)

    # loop through all url's
    for score in box_url:

        # url is the second element of score
        url = score[1]

        # date_id is the third element of score
        date_id = score[2]

        # scrap teams from url
        teams = getTeams(url)

        # scrap tables from url
        tables = getTables(url)

        # insert performance of away team
        insertperformance(tables[0], tables[1], teams[0], teams[1], 0, date_id, cursor, cnx)

        # insert performance of home team
        insertperformance(tables[2], tables[3], teams[1], teams[0], 1, date_id, cursor, cnx)