import mysql.connector
from datetime import datetime, date
import constants

def insertDate(year, month, day, cursor):
    addDate = "INSERT INTO new_dates (date) VALUES(%s)"
    dateData = (date(year, month, day),)

    cursor.execute(addDate, dateData)

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    year = constants.yearP
    month = constants.monthP
    day = constants.dayP

    insertDate(year, month, day, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()