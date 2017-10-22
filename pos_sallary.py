import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests

def scrape_rotoguru(cursor, cnx):
	#empty will be used to scrape from rotoguru csv
	pass



if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    scrape_rotoguru(cursor, cnx)
