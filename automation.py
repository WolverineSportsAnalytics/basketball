import TY_LUE_generate_dates as genDates
import POP_generateBoxScoreURLs as genBox 
import RUSS_perfomanceScraper.py as performScraper
import WARRIORS_team_performance.py as teamPerform
import Le_dailyPerformanceExtrapolation as dailPerEx
import DIRK_teamPerformanceExtrapolation as teamPerEx
import DRAYMOND_teamVsDefenseExtrapolation as teamVsEx
# write sum points into a script so it can be executed from python
import CP3_fanduelScraper as fanScraper
import NASH_fanduelIDManagement as IDmanage
# have to write a script that will pull in and read in the fanduel file as is, so that it can be done without manuelly doint it

'''
In here I will call all in a row and check to see if any of the bugs have been broke

Need to read the consants file to see if we can slim down on any constants.

This should be able to do it all with just one run and will have default be running with the current day
and an optional paremeter if it needs to read from constans, that way if we are actually runnonig it everyday we do not need 
to mess with the constants file everyday

'''

