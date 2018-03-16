# have to write a script that will pull in and read in the fanduel file as is, so that it can be done without manuelly doint it
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


'''
In here I will call all in a row and check to see if any of the bugs have been broke

Need to read the consants file to see if we can slim down on any constants.

This should be able to do it all with just one run and will have default be running with the current day
and an optional paremeter if it needs to read from constans, that way if we are actually runnonig it everyday we do not need 
to mess with the constants file everyday

'''
if __name__ == "__main__":
    
    # first figure out what day it is through some way
    # then query database to get that dateID
    # Now run it all and hope and pray

    # scrape players
    # set start and end date to be equal to current date
    playerRefScraper.auto()

    # generate BoxScoreUrls
    # set start and end date to be equal to current date
    generateBoxScoreURLs.auto()

    # scrape performance data
    # set start and end date to be equal to current date
    perfomanceScraper.auto()
    

    # team performance
    # set start and end date to be equal to current date
    team_performance.auto()

    # daily performance  
    # set dailyPerformanceExtrapolationDateCutOff to be todays date
    # And set upperbound to be today's date
    dailyPerformanceExtrapolation.auto() 

    # team performance  
    # set TeamPerformanceExtrapolationDateCutOff to today date
    # And set upperbound to be today's date
    teamPerformanceExtrapolation.auto() 

    #team vs defense performance  
    # set PerformanceExtrapolationDateCutOff to be todays date
    # And set upperbound to be today's date
    teamVsDefenseExtrapolation.auto() 
    
    
    # Scarape fanduel file
    # going to have to change the entire fanduel scraper to run somewhere else
    newFanduelScraper.auto()

    # get projected minutes
    #dailyMinutes projection
    dailyMinutes.auto()
    
    # run sumPoints
    sumPoints.auto()

    # do current magic to place everyone in futures tables
    currentMagic.auto()
    
    # do projecting
    projMagic.auto()

    # run optimizer
    Optimizer.auto()
    

    '''
    Need global variable for current date 
    Need global variable for dateID
    '''

   
