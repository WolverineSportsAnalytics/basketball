import mysql.connector
import constants

def auto():
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    sumPoints = "update performance set draftkingsPts = (points + 3PM*.5 + totalRebounds*1.25 + steals*2 + blocks*2 -turnovers*.5 + doubleDouble + tripleDouble) where dateID>850"
    sum2 = "update performance set fanduelPts = (FT + totalRebounds*1.2 + assists*1.5 + blocks*3 + steals*3 - turnovers + (3PM)*3 + (fieldGoals-3PM)*2) where dateID>850;"

    joinFDDKPoints = "UPDATE basketball.futures as f INNER JOIN basketball.performance as p ON (f.dateID = p.dateID AND f.playerID = p.playerID) SET f.draftkingsPts = p.draftkingsPts, f.fanduelPts = p.fanduelPts"

    cursor.execute(sumPoints)
    cnx.commit()
    cursor.execute(sum2)
    cnx.commit()
    cursor.execute(joinFDDKPoints)

    cursor.close()
    cnx.commit()
    cnx.close()
    


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    auto()

    cursor.close()
    cnx.commit()
    cnx.close()
