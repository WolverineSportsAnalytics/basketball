import numpy as np
from sklearn.linear_model import Ridge
import mysql.connector
import datetime as dt
import constants

def getDate(day, month, year, cursor):
    gameIDP = 0

    findGame = "SELECT iddates FROM new_dates WHERE date = %s"
    findGameData = (dt.date(year, month, day),)
    cursor.execute(findGame, findGameData)

    for game in cursor:
        gameIDP = game[0]

    return gameIDP

if __name__ == "__main__":

    # dates to retrieve data for batter test data
    # start date
    year = constants.yearP
    month = constants.monthP
    day = constants.dayP

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    dateID = getDate(day, month, year, cursor)

    print "Training Ben Simmons Model..."


    benSimmonsModel = ["projMinutes",
                       "fanduel",
                       "FG_DPA_7",
                       "pointsDPA_7",
                       "FGA_DPA_7",
                       "minutesDPA_7",
                       "turnoversDPA_7",
                       "dReboundDPA_7",
                       "USG_DPA_7",
                       "FTA_DPA_7",
                       "FTP_DPA_7",
                       "totalReboundsDPA_7",
                       "FTM_DPA_7",
                       "AST_DPA_7",
                       "stealsDPA_7",
                       "personalFoulsDPA_7",
                       "doubleDoubleDPA_7",
                       "ASTP_DPA_7",
                       "blocksDPA_7",
                       "oReboundDPA_7",
                       "dReboundP_DPA_7",
                       "oRatingDPA_7",
                       "trueShootingP_DPA_7",
                       "FGP_DPA_7",
                       "tripleDoubleDPA_7",
                       "dRatingDPA_7",
                       "3PA_DPA_7",
                       "totalReboundP_DPA_7",
                       "3PM_DPA_7",
                       "3PointAttemptRateDPA_7",
                       "plusMinusDPA_7",
                       "BLKP_DPA_7",
                       "freeThrowAttemptRateDPA_7",
                       "STP_DPA_7",
                       "ortTvP7",
                       "fgOppTeam7",
                       "oReboundP_DPA_7",
                       "eFG_DPA_7",
                       "drtTvP7",
                       "ftpTvP7",
                       "astpOppTeam7",
                       "fgTeam7",
                       "orpmTvP7",
                       "usgTvP7",
                       "astpTeam7",
                       "astOppTeam7",
                       "tpmTvP7",
                       "fgpTvP7",
                       "astTeam7"]

    lonzoBallModel = ["projMinutes",
                      "FTA_DPA",
                      "usgTvP",
                      "fanduel",
                      "minutesDPA",
                      "AST_DPA",
                      "dReboundDPA",
                      "FG_DPA",
                      "blocksDPA",
                      "stealsDPA",
                      "FGA_DPA",
                      "oReboundDPA",
                      "apmTvP",
                      "pointsDPA",
                      "3PP_DPA",
                      "ftarTeam",
                      "FGP_DPA",
                      "tRebTeam",
                      "astTeam",
                      "trueShootingP_DPA",
                      "STP_DPA",
                      "pfTeam",
                      "fgaTeam",
                      "drtTeam",
                      "dRatingDPA",
                      "3pmTvP",
                      "fgaTvP",
                      "ftaTvP",
                      "paceTeam",
                      "freeThrowAttemptRateDPA",
                      "oRatingDPA",
                      "oReboundP_DPA",
                      "FTM_DPA",
                      "3PA_DPA",
                      "drtTvP",
                      "dReboundsTvP",
                      "blocksTvP",
                      "ftaTeam",
                      "orpTeam",
                      "ftpTvP",
                      "drpTeam",
                      "oRebTeam",
                      "astpTeam",
                      "ASTP_DPA",
                      "tripleDoubleDPA",
                      "orpmTvP",
                      "efgTvP",
                      "trpTeam"]

    getFeaturesB = "SELECT "

    for m in (benSimmonsModel):
        getFeaturesB += m
        getFeaturesB += ", "
    getFeaturesB = getFeaturesB[:-2]
    getFeaturesB += " FROM futures"    # turn into numpy arrays
    getFeaturesB += " WHERE dateID < "
    getFeaturesB += str(dateID)

    getFeaturesL = "SELECT "

    for m in (lonzoBallModel):
        getFeaturesL += m
        getFeaturesL += ", "
    getFeaturesL = getFeaturesL[:-2]
    getFeaturesL += " FROM futures"  # turn into numpy arrays
    getFeaturesL += " WHERE dateID < "
    getFeaturesL += str(dateID)

    allPlayerFeatures = []

    cursor.execute(getFeaturesB)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    FDTargets = []

    getTargets = "SELECT fanduelPts FROM futures WHERE dateID < %s"
    getTargetsData = (dateID,)
    cursor.execute(getTargets, getTargetsData)
    targets = cursor.fetchall()

    for tar in targets:
        FDTargets.append(tar)

    numFeatures = len(allPlayerFeatures[0])
    testXB = np.asarray(allPlayerFeatures)
    testY = np.asarray(FDTargets)

    print "Number of training examples: " + str(np.shape(testXB)[0])

    # add bias term
    ones = np.ones((np.shape(testXB)[0], 1), dtype=float)
    testXB = np.hstack((ones, testXB))

    ridge = Ridge(alpha=9, fit_intercept=True, normalize=True)
    ridge.fit(testXB, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Ben" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)

    print "Training Lonzo Ball Model..."

    allPlayerFeatures = []

    cursor.execute(getFeaturesL)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    numFeatures = len(allPlayerFeatures[0])
    testXL = np.asarray(allPlayerFeatures)

    print "Number of training examples: " + str(np.shape(testXL)[0])

    # add bias term
    ones = np.ones((np.shape(testXL)[0], 1), dtype=float)
    testXL = np.hstack((ones, testXL))

    ridge = Ridge(alpha=9, fit_intercept=True, normalize=True)
    ridge.fit(testXL, testY)
    thetaSKLearnRidge = ridge.coef_
    fileName = 'coef' + "Lonzo" + '.npz'

    outfile = open(fileName, 'w')
    np.save(outfile, thetaSKLearnRidge)