# have to write a script that will pull in and read in the fanduel file as is, so that it can be done without manuelly doint it
import datetime
import mysql
import constants
import generate_dates
import playerRefScraper
import generateBoxScoreURLs
import perfomanceScraper
import team_performance
import dailyPerformanceExtrapolation
import teamPerformanceExtrapolation
import teamVsDefenseExtrapolation 
import pos_sallary
import sumPoints
import fanduelScraper
import newFanduelScraper
import dailyMinutesScraper
import currentMagic
import projMagic
import Optimizer


'''
In here I will call all in a row and check to see if any of the bugs have been broke

Need to read the consants file to see if we can slim down on any constants.

This should be able to do it all with just one run and will have default be running with the current day
and an optional paremeter if it needs to read from constans, that way if we are actually runnonig it everyday we do not need 
to mess with the constants file everyday

'''
if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,                                                                                                                       
                                  host=constants.databaseHost,                                                                                                                       
                                  database=constants.databaseName,                                                                                                                   
                                  password=constants.databasePassword)                                                                                                               
    cursor = cnx.cursor()    
    now = datetime.datetime.now()

    print str(now.year)+ "-" + str(now.month) + "-" + str(now.day)
    date =  str(now.year)+ "-" + str(now.month) + "-" + str(now.day)
    

    # first figure out what day it is through some way
    # get current date 
    findGame = "SELECT iddates FROM new_dates WHERE date = %s"                                                                                                                   
    findGameData = (date,)                                                                                                                                                       
    # then query database to get that dateID
    cursor.execute(findGame, findGameData)   
    dateID = cursor.fetchall()[0][0]
    print dateID
    
    # Now run it all and hope and pray
    
    # fix day - 1

    # scrape players
    # set start and end date to be equal to current date
    print "PlayerRef"
    playerRefScraper.auto(now.day-1, now.month, now.year)

    # generate BoxScoreUrls
    # set start and end date to be equal to current date
    print "Generate Box Score"
    generateBoxScoreURLs.auto(now.day-1, now.month, now.year)

    # scrape performance data
    # set start and end date to be equal to current date
    print "Performance"
    perfomanceScraper.auto(now.day-1, now.month, now.year)

    # team performance
    # set start and end date to be equal to current date
    print "Team Performance"
    team_performance.auto(now.day-1, now.month, now.year)

    # daily performance  
    # set dailyPerformanceExtrapolationDateCutOff to be todays date
    # And set upperbound to be today's date
    print "Performance Exrapotlate"
    dailyPerformanceExtrapolation.auto(dateID) 

    # team performance  
    # set TeamPerformanceExtrapolationDateCutOff to today date
    # And set upperbound to be today's date
    print "Team Performance Exrapotlate"
    teamPerformanceExtrapolation.auto(dateID) 

    #team vs defense performance  
    # set PerformanceExtrapolationDateCutOff to be todays date
    # And set upperbound to be today's date
    print "Team Vs Defense Exrapotlate"
    teamVsDefenseExtrapolation.auto(dateID) 
    
    
    # Scarape fanduel file
    # going to have to change the entire fanduel scraper to run somewhere else
    print "Fanduel Scraping"
    newFanduelScraper.auto(now.day, now.month, now.year)

    # get projected minutes
    #dailyMinutes projection
    print "Minutes Scaping"
    dailyMinutesScraper.auto(dateID)
    
    # run sumPoints
    sumPoints.auto(now.day-1, now.month, now.year)

    # need to update futures tables for yesterday

    # do current magic to place everyone in futures tables
    print "Current Magic"
    currentMagic.auto(now.day, now.month, now.year)
    
    
    # do projecting
    projMagic.auto(now.day, now.month, now.year)

    # run optimizer
    Optimizer.auto(now.day, now.month, now.year)
    

    '''
    Need global variable for current date 
    Need global variable for dateID
    '''

   
