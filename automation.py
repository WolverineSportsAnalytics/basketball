#!/usr/bin/python2
''' Automate of running WSA Engine '''
import mysql.connector
import datetime
from Scrapers import teamPerformance
from Scrapers import performance
from Scrapers import generateBoxScoreUrls
from Scrapers import playerReference
from Scrapers import fanduel_scraper
from Scrapers import moneyLine
from Extrapilators import dailyPerformanceExtrapolation, teamPerformanceExtrapolation, teamVsDefenseExtrapolation
from Extrapilators import sumPoints, fill_features
from MachineLearning import predict


def main():
    ''' Script to automate running of all basketball engine daily '''
    run_scrapers()

def run_scrapers():
    ''' Run the scrapers '''
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    cursor = cnx.cursor()
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)

    print(str(now.year)+ "-" + str(now.month) + "-" + str(now.day))
    date =  str(now.year)+ "-" + str(now.month) + "-" + str(now.day)


    # first figure out what day it is through some way
    # get current date
    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (date,)
    # then query database to get that dateI
    cursor.execute(findGame, findGameData)
    dateID = cursor.fetchall()[0][0]

    # run player reference scaper
    playerReference.scrapeHtml(cursor, cnx)

    # run generate box score urls
    generateBoxScoreUrls.generateBasketballReferenceURLs(cursor, cnx, yesterday.year, yesterday.month, yesterday.day)
    # run performance
    print("Running Perforamnce DateID:", dateID-1)
    performance.updateAndInsertPlayerRef(yesterday.day, yesterday.month, yesterday.year, yesterday.day, yesterday.month, yesterday.year, cursor, cnx)

    # run team performance
    print("Running Team Performance DateID:", dateID-1)
    teamPerformance.statsFiller(yesterday.day, yesterday.month, yesterday.year, yesterday.day, yesterday.month, yesterday.year, cnx, cursor)

    print("Extrapolating:", dateID)
    dailyPerformanceExtrapolation.auto(dateID,cnx, cursor)
    teamPerformanceExtrapolation.auto(dateID, cnx, cursor)
    teamVsDefenseExtrapolation.auto(dateID, cnx, cursor)


    # sum fanduel and draftkings points
    sumPoints.sum_points(dateID, cursor, cnx)

    # starts the prediction section

    # fandual scraper
    fanduel_scraper.insert_into_performance(cursor, cnx, dateID)

    # money scraper
    moneyLine.clear_table(cursor, cnx)
    moneyLine.InsertGameOdds(cursor, cnx, 16, 10, 2018, yesterday.day, yesterday.month, yesterday.year)
    moneyLine.InsertGameSpread(cursor, cnx, 16, 10, 2018, yesterday.day, yesterday.month, yesterday.year)

    # fill fetaures
    fill_features.fill_futures(dateID, cnx, cursor)


    # machine learning stuff
    predict.makeProjections(now.day, now.month, now.year, cursor, cnx)

if __name__=="__main__":
    main()
