import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests
import datetime as dt
import numpy as np

def updateAndInsertPlayerRef(
        startDay,
        startMonth,
        startYear,
        endDay,
        endMonth,
        endYear,
        cursor,
        cnx):

    
        select_columns = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME =\"futures\""
        cursor.execute(select_columns)
        select_features = "Select * from futures where dateID = %s and playerID = %s"
        print "PlayerID: "
        playerID = raw_input()
        print "DateID: "
        dateID = raw_input()

        columns  = cursor.fetchall()

        cursor.execute(select_features, (dateID, playerID))
        features = cursor.fetchall()

        outfile = open('coef.npz', 'r')
        coefficents = np.load(outfile)


        i = 0
        importance = []
        for column in columns:
            if i > 2 and i < 456:
                print i, column[0], features[0][i], coefficents[0][i-3], " ", features[0][i] * coefficents[0][i-3]
                importance.append((column[0], features[0][i] * coefficents[0][i-3]))
            i = i+1
        
        sorted_importance = sorted(importance, key=lambda tup: tup[1])
        
        total = 0

        for i in range(len(sorted_importance)):
            cat, points = sorted_importance[len(sorted_importance) -1 -i ]
            print cat, points 

            total = total + points

        print "total: ", total


        cursor.close()
        cnx.commit()
        cnx.close()


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
        cursor,
        cnx)
 
