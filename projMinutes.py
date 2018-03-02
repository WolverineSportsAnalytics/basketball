import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests
import csv
import traceback

def auto():
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    projMins = "UPDATE performance as p
SET projMinutes = (
        SELECT minutes FROM player_seven_daily_avg as d
    WHERE p.dateID = d.dateID AND p.playerID = d.playerID)
WHERE projMinutes IS NULL;"

    cursor.execute(projMins)

    cursor.close()
    cnx.commit()
    cnx.close()
    


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    scrape_rotoguru(cursor, cnx)

    cursor.close()
    cnx.commit()
    cnx.close()
