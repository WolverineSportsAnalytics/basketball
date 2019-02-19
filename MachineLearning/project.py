from ridgeRegression import ridgeRegression
from Scrapers import performance
import mysql.connector


def projectById(startdateid, enddateid, cursor):
    getAllData = "select * from futures where fanduelPts is not null and dateID < " + \
        enddateid + " and dateID >= " + startdateid + " ;"
    cursor.execute(getAllData)

    # matrix where each row is a feature for each player
    features = [list(feature) for feature in cursor.fetchall()]

    # How you would import and use ridge regression
    ridge = ridgeRegression(features)
    # returns array of fanduel pt predictions mapping one to one with features
    predictions = ridge.predict()

    # new object with list of tuples of (playerid, dateid, projection)
    result = []
    for i in range(len(predictions)):
        result.append((features[i][1], features[i][2], predictions[i]))

    return result


def insertproject(predictions, nameOfCol, cursor):
    for tuples in predictions:
        insertData = "UPDATE performance SET " + nameOfCol + " = " + \
            tuples[2] + " WHERE playerID = " + tuples[0] + " AND dateID = " + tuples[1] + ";"
        cursor.execute(insertData)


def project(
        startDay,
        startMonth,
        startYear,
        endDay,
        endMonth,
        endYear,
        cursor):

    startid = performance.getDate(startDay, startMonth, startYear, cursor)
    endid = performance.getDate(endDay, endMonth, endYear, cursor)

    prediction = projectById(startid, endid, cursor)

    # prediction returns tuples of (playerid, dateid, prediction)

    nameOfModel = ""
    check = "SELECT " + nameOfModel + \
        " FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA =basetball AND TABLE_NAME =performance;"
    addCol = "ALTER TABLE performance ADD " + nameOfModel + " float;"

    cursor.execute(check)
    cursor.execute(addCol)

    insertproject(prediction, nameOfModel, cursor)
