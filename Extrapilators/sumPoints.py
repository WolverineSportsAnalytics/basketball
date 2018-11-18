import mysql.connector
import constants
import datetime as dt

def sum_points(dateID, cursor, cnx):
    sumPoints = "update performance set draftkingsPts = (points + 3PM*.5 + totalRebounds*1.25 + steals*2 + blocks*2 -turnovers*.5 + doubleDouble + tripleDouble) where dateID = %s"
    sum2 = "update performance set fanduelPts = (FT + totalRebounds*1.2 + assists*1.5 + blocks*3 + steals*3 - turnovers + (3PM)*3 + (fieldGoals-3PM)*2) where dateID = %s"

    joinFDDKPoints = "UPDATE basketball.futures as f INNER JOIN basketball.performance as p ON (f.dateID = p.dateID AND f.playerID = p.playerID) SET f.draftkingsPts = p.draftkingsPts, f.fanduelPts = p.fanduelPts WHERE p.dateID = %s AND f.dateID = %s"

    dateToJoin = dateID -1
    joinData = (dateToJoin,)
    joinJoinData = (dateToJoin, dateToJoin)
    cursor.execute(sumPoints, joinData)
    print "Updated Draftkings Points"
    cnx.commit()
    cursor.execute(sum2, joinData)
    print "Updated FanDuel Points"
    cnx.commit()
    cursor.execute(joinFDDKPoints, joinJoinData)
    print "Updated Futures DK and FD Points"

    cursor.close()
    cnx.commit()
    cnx.close()
    
