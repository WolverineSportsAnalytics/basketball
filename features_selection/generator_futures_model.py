import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
from sklearn.model_selection import cross_val_score
import urllib2
import requests
import datetime as dt
import numpy as np
from sklearn.linear_model import Ridge, Lasso, LinearRegression

featureArray = ["projMinutes",
"fanduel",
"FG_DPA",
"pointsDPA",
"FGA_DPA",
"minutesDPA",
"USG_DPA",
"FTP_DPA",
"turnoversDPA",
"dReboundDPA",
"personalFoulsDPA",
"trueShootingP_DPA",
"oRatingDPA",
"FGP_DPA",
"eFG_DPA",
"totalReboundsDPA",
"FTA_DPA",
"fgOppTeam",
"fgTeam",
"ortOppTeam",
"ortTeam",
"avgPointsScoredOppTeam",
"avgPointsScoredTeam",
"fgaOppTeam",
"fgaTeam",
"fgpOppTeam",
"fgpTeam",
"trpOppTeam",
"trpTeam",
"tspOppTeam",
"tspTeam",
"efgpOppTeam",
"efgpTeam",
"paceOppTeam",
"paceTeam",
"drtOppTeam",
"drtTeam",
"drpOppTeam",
"drpTeam",
"tRebOppTeam",
"tRebTeam",
"avgPointsAllowedOppTeam",
"avgPointsAllowedTeam",
"tsTvP",
"dRebOppTeam",
"dRebTeam",
"efgTvP",
"ftpOppTeam",
"ftpTeam",
"fgpTvP",
"3ppOppTeam",
"3ppTeam",
"astpOppTeam",
"astpTeam",
"ppmTvP",
"astOppTeam",
"astTeam",
"pfOppTeam",
"pfTeam",
"ftaOppTeam",
"ftaTeam",
"dRatingDPA",
"ftpTvP",
"turnoverpOppTeam",
"turnoverpTeam",
"orpOppTeam",
"orpTeam",
"ftOppTeam",
"ftTeam",
"stlpOppTeam",
"stlpTeam",
"stlOppTeam",
"stlTeam",
"ftperfgaOppTeam",
"ftperfgaTeam",
"turnoversOppTeam",
"turnoversTeam",
"oRebOppTeam",
"oRebTeam",
"3ppTvP",
"stealsDPA",
"3paOppTeam",
"3paTeam",
"3parOppTeam",
"3parTeam",
"tpmTvP",
"blkpOppTeam",
"blkpTeam",
"3pOppTeam",
"3pTeam",
"blocksOppTeam",
"blocksTeam",
"FTM_DPA",
"dReboundP_DPA",
"spmTvP",
"ftarOppTeam",
"ftarTeam",
"drpmTvP",
"ortTvP",
"drtTvP",
"usgTvP",
"apmTvP",
"totalReboundP_DPA",
"AST_DPA",
"ASTP_DPA",
"turnoverP_DPA",
"STP_DPA",
"freeThrowAttemptRateDPA",
"ddpgTvP",
"3PP_DPA",
"3PA_DPA",
"oReboundDPA",
"3PM_DPA",
"orpmTvP",
"tReboundsTvP",
"dReboundsTvP",
"blocksDPA",
"ftaTvP",
"bpmTvP",
"fgTvP",
"oReboundsTvP",
"minutesTvP",
"blocksTvP",
"pointsTvP",
"ftTvP",
"turnoversTvP",
"winsOppTeam",
"winsTeam",
"fgaTvP",
"lossesOppTeam",
"lossesTeam",
"stealsTvP",
"ddTvP",
"oReboundP_DPA",
"3PointAttemptRateDPA",
"assistsTvP",
"3paTvP",
"3pmTvP",
"BLKP_DPA",
"doubleDoubleDPA",
"dddTvP",
"dddpgTvP",
"tripleDoubleDPA",
"plusMinusDPA"]

def hitDaGenerator(cursor):
    finalFeature = "fanduelPts"
    models = []
    mScores = []
    featureChange = {}


    for counter, x in enumerate(featureArray):
        model = []
        for mini, y in enumerate(range(counter + 1)):
            model.append(featureArray[mini])
        statement = "SELECT "
        for feature in model:
            statement += feature
            statement += ", "
        statement = statement[:-2]
        statement += " "
        statement += " FROM futures"
        models.append(model)
        cursor.execute(statement)

        allPlayerFeatures = []
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
        testX = np.asarray(allPlayerFeatures)
        testY = np.asarray(FDTargets)

        print "Number of training examples: " + str(np.shape(testX)[0])
        print "Model: " + str(model)
        print "Target is " + finalFeature

        # add bias term
        ones = np.ones((np.shape(testX)[0], 1), dtype=float)
        testX = np.hstack((ones, testX))

        # cross validate! + get the best score!

        ridge = Ridge(alpha=9, fit_intercept=True, normalize=True)

        scores = cross_val_score(ridge, testX, testY, scoring='neg_mean_squared_error', cv=7)

        # This will print the mean of the list of errors that were output and
        # provide your metric for evaluation
        print "The average mse for this model is :" + str(scores.mean())
        mScores.append(scores.mean())
        if counter >= 1:
            print "The change by adding: " + str(featureArray[counter]) + " is " + str((mScores[counter - 1] - mScores[counter]))
            featureChange[featureArray[counter]] = (mScores[counter] - mScores[counter - 1])
        print str(featureChange)


    return featureChange

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    test = False

    if test:
        featureDictionary = hitDaGenerator(cursor)

        for w in sorted(featureDictionary, key=featureDictionary.get, reverse=True):
            print w, featureDictionary[w]
    else:
        actualModel = ["projMinutes",
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
        actualEvansModel = ["projMinutes",
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

        print "Beast " + str(sorted(actualModel, key=str.lower))
        print "Beast Size " + str(len(actualModel))
        print "Evan " + str(sorted(actualEvansModel, key=str.lower))
        print "Evan's Size " + str(len(actualEvansModel))


        statement = "SELECT "
        for m in (actualEvansModel):
            statement += m
            statement += ", "
        statement = statement[:-2]
        statement += " FROM futures"

        cursor.execute(statement)

        allPlayerFeatures = []
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
        testX = np.asarray(allPlayerFeatures)
        testY = np.asarray(FDTargets)

        print "Number of training examples: " + str(np.shape(testX)[0])
        print "Model: " + str(actualModel)
        print "Target is " + "fanduelPts"

        # add bias term
        ones = np.ones((np.shape(testX)[0], 1), dtype=float)
        testX = np.hstack((ones, testX))

        # cross validate! + get the best score!

        ridge = Ridge(alpha=1, fit_intercept=True, normalize=True)

        scores = cross_val_score(ridge, testX, testY, scoring='neg_mean_squared_error', cv=7)

        # This will print the mean of the list of errors that were output and
        # provide your metric for evaluation
        print "The average mse for this model is :" + str(scores.mean())
