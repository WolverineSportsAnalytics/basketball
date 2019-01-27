from ridgeRegression import ridgeRegression
from Scrapers import performance
import mysql.connector

def projectById(startdateid, enddateid, cursor):
    getAllData = "select * from futures where fanduelPts is not null"
    cursor.execute(getAllData)

    features = [list(feature) for feature in cursor.fetchall()]


    # How you would import and us ridge regression
    ridge = ridgeRegression(features)
    predictions = ridge.predict()
    return predictions

def insertproject(predictions):


def project(startDay, startMonth, startYear, endDay, endMonth, endYear):
    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)

    startid = performance.getDate(startDay, startMonth, startYear, cursor)
    endid = performance.getDate(endDay, endMonth, endYear, cursor)

    prediction = projectById(startid, endid, cursor)

    # prediction returns tuples of (playerid, prediction)

    nameOfModel = ""
    check = "SELECT " + nameOfModel + " FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA =basetball AND TABLE_NAME =performance;"
    addCol = "ALTER TABLE performance ADD " + nameOfModel + " float;"


