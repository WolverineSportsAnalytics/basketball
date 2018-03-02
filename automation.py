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
    # generate dates

    #generate_dates.auto() 

    # scrape players
    #playerRefScraper.auto()

    # generate BoxScoreUrls
    # generateBoxScoreURLs.auto()

    # scrape performance data
    perfomanceScraper.auto()
    
    # team performance
    team_performance.auto()
    print "All players scraped"

    exit(1)
    # daily performance  
    dailyPerformanceExtrapolation.auto() 

    # team performance  
    teamPerformanceExtrapolation.auto() 

    #  team vs defense performance  
    teamVsDefenseExtrapolation.auto() 
    
    # use rotguru to enter into pos sallary 
    # pos_sallary.auto()

    # run sumPoints
    sumPoints.auto()

    # Scarape fanduel file
    fanduelScraper.auto()

    # get projected minutes
    projMinutes.auto()

    # do projecting
    projMagic.auto()

    # run optimizer
    optimizer.auto()
    


   
