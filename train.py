import numpy as np
import scipy as sp
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge, LinearRegression
import pandas as pd
import mysql.connector
import os
import datetime as dt
from itertools import chain
import constants
import warnings
from tempfile import TemporaryFile

if __name__ == "__main__":
    getFeatures = "SELECT fanduel, blocksDPA,  pointsDPA ,  stealsDPA ,  AST_DPA ,  turnoversDPA ,  totalReboundsDPA ,  tripleDoubleDPA ,  doubleDoubleDPA ,  3PM_DPA ,  oReboundDPA ,  dReboundDPA ,  minutesDPA ,  FG_DPA ,  FGA_DPA ,  FGP_DPA ,  3PA_DPA ,  3PP_DPA ,  FTM_DPA ,  FTA_DPA ,  FTP_DPA ,  personalFoulsDPA ,  plusMinusDPA ,  trueShootingP_DPA ,  eFG_DPA ,  freeThrowAttemptRateDPA ,  3PointAttemptRateDPA ,  oReboundP_DPA ,  dReboundP_DPA ,  totalReboundP_DPA ,  ASTP_DPA ,  STP_DPA ,  BLKP_DPA ,  turnoverP_DPA ,  USG_DPA ,  oRatingDPA ,  dRatingDPA ,  blocksDPA_7 ,  pointsDPA_7 ,  stealsDPA_7 ,  AST_DPA_7 ,  turnoversDPA_7 ,  totalReboundsDPA_7 ,  tripleDoubleDPA_7 ,  doubleDoubleDPA_7 ,  3PM_DPA_7 ,  oReboundDPA_7 ,  dReboundDPA_7 ,  minutesDPA_7 ,  FG_DPA_7 ,  FGA_DPA_7 ,  FGP_DPA_7 ,  3PA_DPA_7 ,  3PP_DPA_7 ,  FTM_DPA_7 ,  FTA_DPA_7 ,  FTP_DPA_7 ,  personalFoulsDPA_7 ,  plusMinusDPA_7 ,  trueShootingP_DPA_7 ,  eFG_DPA_7 ,  freeThrowAttemptRateDPA_7 ,  3PointAttemptRateDPA_7 ,  oReboundP_DPA_7 ,  dReboundP_DPA_7 ,  totalReboundP_DPA_7 ,  ASTP_DPA_7 ,  STP_DPA_7 ,  BLKP_DPA_7 ,  turnoverP_DPA_7 ,  USG_DPA_7 ,  oRatingDPA_7 ,  dRatingDPA_7 ,  blocksDPA_21 ,  pointsDPA_21 ,  stealsDPA_21 ,  AST_DPA_21 ,  turnoversDPA_21 ,  totalReboundsDPA_21 ,  tripleDoubleDPA_21 ,  doubleDoubleDPA_21 ,  3PM_DPA_21 ,  oReboundDPA_21 ,  dReboundDPA_21 ,  minutesDPA_21 ,  FG_DPA_21 ,  FGA_DPA_21 ,  FGP_DPA_21 ,  3PA_DPA_21 ,  3PP_DPA_21 ,  FTM_DPA_21 ,  FTA_DPA_21 ,  FTP_DPA_21 ,  personalFoulsDPA_21 ,  plusMinusDPA_21 ,  trueShootingP_DPA_21 ,  eFG_DPA_21 ,  freeThrowAttemptRateDPA_21 ,  3PointAttemptRateDPA_21 ,  oReboundP_DPA_21 ,  dReboundP_DPA_21 ,  totalReboundP_DPA_21 ,  ASTP_DPA_21 ,  STP_DPA_21 ,  BLKP_DPA_21 ,  turnoverP_DPA_21 ,  USG_DPA_21 ,  oRatingDPA_21 ,  dRatingDPA_21 ,  winsTeam ,  winsTeam7 ,  winsTeam21 ,  lossesTeam ,  lossesTeam7 ,  lossesTeam21 ,  ortTeam ,  ortTeam7 ,  ortTeam21 ,  drtTeam ,  drtTeam7 ,  drtTeam21 ,  avgPointsAllowedTeam ,  avgPointsAllowedTeam7 ,  avgPointsAllowed21 ,  avgPointsScoredTeam ,  avgPointsScoredTeam7 ,  avgPointsScoredTeam21 ,  paceTeam ,  paceTeam7 ,  paceTeam21 ,  efgpTeam ,  efgpTeam7 ,  efgpTeam21 ,  turnoverpTeam ,  turnoverpTeam7 ,  turnoverpTeam21 ,  orpTeam ,  orpTeam7 ,  orpTeam21 ,  ftperfgaTeam ,  ftperfgaTeam7 ,  ftperfgaTeam21 ,  fgTeam ,  fgTeam7 ,  fgTeam21 ,  fgaTeam ,  fgaTeam7 ,  fgaTeam21 ,  fgpTeam ,  fgpTeam7 ,  fgpTeam21 ,  3pTeam ,  3pTeam7 ,  3pTeam21 ,  3paTeam ,  3paTeam7 ,  3paTeam21 ,  3ppTeam ,  3ppTeam7 ,  3ppTeam21 ,  ftTeam ,  ftTeam7 ,  ftTeam21 ,  ftaTeam ,  ftaTeam7 ,  ftaTeam21 ,  ftpTeam ,  ftpTeam7 ,  ftpTeam21 ,  oRebTeam ,  oRebTeam7 ,  oRebTeam21 ,  dRebTeam ,  dRebTeam7 ,  dRebTeam21 ,  tRebTeam ,  tRebTeam7 ,  tRebTeam21 ,  astTeam ,  astTeam7 ,  astTeam21 ,  stlTeam ,  stlTeam7 ,  stlTeam21 ,  blocksTeam ,  blocksTeam7 ,  blocksTeam21 ,  turnoversTeam ,  turnoversTeam7 ,  turnoversTeam21 ,  pfTeam ,  pfTeam7 ,  pfTeam21 ,  tspTeam ,  tspTeam7 ,  tspTeam21 ,  3parTeam ,  3parTeam7 ,  3parTeam21 ,  ftarTeam ,  ftarTeam7 ,  ftarTeam21 ,  drpTeam ,  drpTeam7 ,  drpTeam21 ,  trpTeam ,  trpTeam7 ,  trpTeam21 ,  astpTeam ,  astpTeam7 ,  astpTeam21 ,  stlpTeam ,  stlpTeam7 ,  stlpTeam21 ,  blkpTeam ,  blkpTeam7 ,  blkpTeam21 ,  points1qTeam ,  points1qTeam7 ,  points1qTeam21 ,  points2qTeam ,  points2qTeam7 ,  points2qTeam21 ,  points3qTeam ,  points3qTeam7 ,  points3qTeam21 ,  points4qTeam ,  points4qTeam7 ,  points4qTeam21 ,  winsOppTeam ,  winsOppTeam7 ,  winsOppTeam21 ,  lossesOppTeam ,  lossesOppTeam7 ,  lossesOppTeam21 ,  ortOppTeam ,  ortOppTeam7 ,  ortOppTeam21 ,  drtOppTeam ,  drtOppTeam7 ,  drtOppTeam21 ,  avgPointsAllowedOppTeam ,  avgPointsAllowedOppTeam7 ,  avgPointsAllowedOpp21 ,  avgPointsScoredOppTeam ,  avgPointsScoredOppTeam7 ,  avgPointsScoredOppTeam21 ,  paceOppTeam ,  paceOppTeam7 ,  paceOppTeam21 ,  efgpOppTeam ,  efgpOppTeam7 ,  efgpOppTeam21 ,  turnoverpOppTeam ,  turnoverpOppTeam7 ,  turnoverpOppTeam21 ,  orpOppTeam ,  orpOppTeam7 ,  orpOppTeam21 ,  ftperfgaOppTeam ,  ftperfgaOppTeam7 ,  ftperfgaOppTeam21 ,  fgOppTeam ,  fgOppTeam7 ,  fgOppTeam21 ,  fgaOppTeam ,  fgaOppTeam7 ,  fgaOppTeam21 ,  fgpOppTeam ,  fgpOppTeam7 ,  fgpOppTeam21 ,  3pOppTeam ,  3pOppTeam7 ,  3pOppTeam21 ,  3paOppTeam ,  3paOppTeam7 ,  3paOppTeam21 ,  3ppOppTeam ,  3ppOppTeam7 ,  3ppOppTeam21 ,  ftOppTeam ,  ftOppTeam7 ,  ftOppTeam21 ,  ftaOppTeam ,  ftaOppTeam7 ,  ftaOppTeam21 ,  ftpOppTeam ,  ftpOppTeam7 ,  ftpOppTeam21 ,  oRebOppTeam ,  oRebOppTeam7 ,  oRebOppTeam21 ,  dRebOppTeam ,  dRebOppTeam7 ,  dRebOppTeam21 ,  tRebOppTeam ,  tRebOppTeam7 ,  tRebOppTeam21 ,  astOppTeam ,  astOppTeam7 ,  astOppTeam21 ,  stlOppTeam ,  stlOppTeam7 ,  stlOppTeam21 ,  blocksOppTeam ,  blocksOppTeam7 ,  blocksOppTeam21 ,  turnoversOppTeam ,  turnoversOppTeam7 ,  turnoversOppTeam21 ,  pfOppTeam ,  pfOppTeam7 ,  pfOppTeam21 ,  tspOppTeam ,  tspOppTeam7 ,  tspOppTeam21 ,  3parOppTeam ,  3parOppTeam7 ,  3parOppTeam21 ,  ftarOppTeam ,  ftarOppTeam7 ,  ftarOppTeam21 ,  drpOppTeam ,  drpOppTeam7 ,  drpOppTeam21 ,  trpOppTeam ,  trpOppTeam7 ,  trpOppTeam21 ,  astpOppTeam ,  astpOppTeam7 ,  astpOppTeam21 ,  stlpOppTeam ,  stlpOppTeam7 ,  stlpOppTeam21 ,  blkpOppTeam ,  blkpOppTeam7 ,  blkpOppTeam21 ,  points1qOppTeam ,  points1qOppTeam7 ,  points1qOppTeam21 ,  points2qOppTeam ,  points2qOppTeam7 ,  points2qOppTeam21 ,  points3qOppTeam ,  points3qOppTeam7 ,  points3qOppTeam21 ,  points4qOppTeam ,  points4qOppTeam7 ,  points4qOppTeam21 ,  blocksTvP ,  pointsTvP ,  stealsTvP ,  assistsTvP ,  turnoversTvP ,  tReboundsTvP ,  dddTvP ,  ddTvP ,  3pmTvP ,  3paTvP ,  oReboundsTvP ,  dReboundsTvP ,  minutesTvP ,  fgTvP ,  fgaTvP ,  ftTvP ,  ftaTvP ,  bpmTvP ,  ppmTvP ,  spmTvP ,  apmTvP ,  tpmTvP ,  dddpgTvP ,  ddpgTvP ,  3ppTvP ,  orpmTvP ,  drpmTvP ,  fgpTvP ,  ftpTvP ,  usgTvP ,  ortTvP ,  drtTvP ,  tsTvP ,  efgTvP ,  blocksTvP7 ,  pointsTvP7 ,  stealsTvP7 ,  assistsTvP7 ,  turnoversTvP7 ,  tReboundsTvP7 ,  dddTvP7 ,  ddTvP7 ,  3pmTvP7 ,  3paTvP7 ,  oReboundsTvP7 ,  dReboundsTvP7 ,  minutesTvP7 ,  fgTvP7 ,  fgaTvP7 ,  ftTvP7 ,  ftaTvP7 ,  bpmTvP7 ,  ppmTvP7 ,  spmTvP7 ,  apmTvP7 ,  tpmTvP7 ,  dddpgTvP7 ,  ddpgTvP7 ,  3ppTvP7 ,  orpmTvP7 ,  drpmTvP7 ,  fgpTvP7 ,  ftpTvP7 ,  usgTvP7 ,  ortTvP7 ,  drtTvP7 ,  tsTvP7 ,  efgTvP7 ,  blocksTvP21 ,  pointsTvP21 ,  stealsTvP21 ,  assistsTvP21 ,  turnoversTvP21 ,  tReboundsTvP21 ,  dddTvP21 ,  ddTvP21 ,  3pmTvP21 ,  3paTvP21 ,  oReboundsTvP21 ,  dReboundsTvP21 ,  minutesTvP21 ,  fgTvP21 ,  fgaTvP21 ,  ftTvP21 ,  ftaTvP21 ,  bpmTvP21 ,  ppmTvP21 ,  spmTvP21 ,  apmTvP21 ,  tpmTvP21 ,  dddpgTvP21 ,  ddpgTvP21 ,  3ppTvP21 ,  orpmTvP21 ,  drpmTvP21 ,  fgpTvP21 ,  ftpTvP21 ,  usgTvP21 ,  ortTvP21 ,  drtTvP21 ,  tsTvP21 , efgTvP21 FROM futures;"
    # turn into numpy arrays
    allPlayerFeatures = []

    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor()

    cursor.execute(getFeatures)

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

    # add bias term
    ones = np.ones((np.shape(testX)[0], 1), dtype=float)
    testX = np.hstack((ones, testX))

    # learning rate + iterations
    alpha = 0.01
    num_iters = 1000

    # theta initialization
    theta = np.zeros(((numFeatures + 1), 1))
    theta = np.transpose(theta)

    coefficents = TemporaryFile()

    ridge = Ridge(alpha=1, fit_intercept=False, normalize=True)
    ridge.fit(testX, testY)
    thetaSKLearnRidge = ridge.coef_

    outfile = open('coef.npz', 'w')
    np.save(outfile, thetaSKLearnRidge)

    print "Player Theta Values from Sklearn Ridge Regression"
    print thetaSKLearnRidge