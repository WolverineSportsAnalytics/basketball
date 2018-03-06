import numpy as np
import scipy as sp
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge, Lasso, LinearRegression
import pandas as pd
import mysql.connector
import os
import datetime as dt
from itertools import chain
import constants
import warnings
from tempfile import TemporaryFile

if __name__ == "__main__":

    print "Training Ben Simmons Model..."

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    benSimmonsModel = ["projMinutes",
                       "fanduel",
                       "FG_DPA",
                       "pointsDPA",
                       "FGA_DPA",
                       "minutesDPA",
                       "turnoversDPA",
                       "dReboundDPA",
                       "USG_DPA",
                       "FTA_DPA",
                       "FTP_DPA",
                       "totalReboundsDPA",
                       "FTM_DPA",
                       "AST_DPA",
                       "stealsDPA",
                       "personalFoulsDPA",
                       "doubleDoubleDPA",
                       "ASTP_DPA",
                       "blocksDPA",
                       "oReboundDPA",
                       "dReboundP_DPA",
                       "oRatingDPA",
                       "trueShootingP_DPA",
                       "FGP_DPA",
                       "tripleDoubleDPA",
                       "dRatingDPA",
                       "3PA_DPA",
                       "totalReboundP_DPA",
                       "3PM_DPA",
                       "3PointAttemptRateDPA",
                       "plusMinusDPA",
                       "BLKP_DPA",
                       "freeThrowAttemptRateDPA",
                       "STP_DPA",
                       "ortTvP",
                       "fgOppTeam",
                       "oReboundP_DPA",
                       "eFG_DPA",
                       "drtTvP",
                       "ftpTvP",
                       "astpOppTeam",
                       "fgTeam",
                       "orpmTvP",
                       "usgTvP",
                       "astpTeam",
                       "astOppTeam",
                       "tpmTvP",
                       "fgpTvP",
                       "astTeam"]

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

    getFeaturesL = "SELECT "

    for m in (lonzoBallModel):
        getFeaturesL += m
        getFeaturesL += ", "
    getFeaturesL = getFeaturesL[:-2]
    getFeaturesL += " FROM futures"  # turn into numpy arrays

    allPlayerFeatures = []

    cursor.execute(getFeaturesB)

    features = cursor.fetchall()
    for feat in features:
        allPlayerFeatures.append(feat)

    FDTargets = []

    getTargets = "SELECT fanduelPts FROM futures"
    cursor.execute(getTargets)
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