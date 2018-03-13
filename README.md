# Contributors:
    - Jake Becker
    - Evan Ciancio
    - Phillip Mathew
    - Justin Liss
    - Sri Garlapati
    - Brendan Hart

# Trust the Process:

### Run the generate_dates.py
	- Job: Loads any new dates into the new_dates table from the range that was specified
	- Configure startYearP, startMonthP, startDayP or endYearP, endMonthP, or endDayP to correspond to the dates from
	which you want to pull new dates
		- [(startYearP, startMonthP, startDayP), (endYearP, endMonthP, and endDayP))
			- inclusive of start date, exclusive of end date
	- To run generate_dates.py for one day, the endDate should be one day ahead of the startDate
	- Could probably just run this once and generate all the dates for a basketball season
	- Note: only run if date is not in table!

### Run the playerRefScraper.py
	- Job: Loads any new players into the player reference table that have played the night or season or whenever 
	before
	- Configure startYearP, startMonthP, startDayP or endYearP, endMonthP, or endDayP to correspond to the dates from
	which you want to pull new players from basketball reference 
		- [(startYearP, startMonthP, startDayP), (endYearP, endMonthP, and endDayP)]
			- inclusive of start date, inclusive of end date

### Run generateBoxScoreURLs.py
	- Job: Loads potential Box Score URLs into the database from the specified date range in constants.py so that the
	performance scraper can pull in all of data from the box score
	- Configure startYearP, startMonthP, startDayP or endYearP, endMonthP, or endDayP to correspond to the dates from
	which you want to pull new potential box score URLS from basketball reference
		- [(startYearP, startMonthP, startDayP), (endYearP, endMonthP, and endDayP)]
			- inclusive of start date, inclusive of end date
			
### Run performanceScraper.py
	- Job: Scrape the box score data and put it into player performance table
	- Configure startYearP, startMonthP, startDayP or endYearP, endMonthP, or endDayP to correspond to the dates 
	from which you want to pull the box scores URLS from the database to scrape the data
		- [(startYearP, startMonthP, startDayP), (endYearP, endMonthP, and endDayP)]
			- inclusive of start date, inclusive of end date
    - Cleans up any players who did not play

### Run team_performance.py
	- Job: Scrape the box score data and put it into team performance table
	- Configure startYearP, startMonthP, startDayP or endYearP, endMonthP, or endDayP to correspond to the dates 
	from which you want to pull the box scores URLS from the database to scrape the data
		- [(startYearP, startMonthP, startDayP), (endYearP, endMonthP, and endDayP))
			- inclusive of start date, exclusive of end date

### Download new rotoguru file
	- Download from rotoguru.com, go to Daily Hoops Data under Basketball on the left toolbar, then go to Other Tools, then click on 2017-18 Master File
	- Copy all the data and move into rotoguru20172018data.csv
	- Delimite by comma (,) and colon (:)
		- Highlight the first column
		- Data > Text to Columns > Delimited > Comma, ":" > Finish
		- Save it as a Windows CSV
	- Filter only the days you need
		○ Note: only need to run when didn't pull FanDuel information from FanDuel competition

### If need to run rotoguru file, Run rotoguruIDManagement.py
    - Job: align the rotoguru player ID with the basketball reference id

### If need to run rotoguru file, Run pos_sallary.py
	- Job: put the fanduel and draftkings position and salary into the performance table

### Run the extrapolators!
	- Job: Extrapolate the data scraped from the performance tables to the average tables to get a player's average
	for a season on that day, a team's average for a season on that day, and a team's result vs a defense on that day
	- For all extrapolators, the upper and lower bounds for the dateID's are inclusive
	- How:
		○ Run dailyPerformanceExtrapolation.py
			§ Specify the date id for which you want to extrapolate the data according to the first day for
			which you have not scraped data all the way till the day you are predicting in constants.py 
			(specify date id)
		○ Run teamPerformanceExtrapolation.py
			§ Specify the date id for which you want to extrapolate the data according to the first day
			for which you have not scraped data all the way till the day you are predicting in constants.py
			(specify date id)
		○ Run teamVsDefenseExtrapolation.py
			§ Specify the date id for which you want to extrapolate the data according to the first day for
			which you have not scraped data all the way till the day you are predicting in constants.py
			(specify date id)
        ○ When setting the date ids, know that it is inclusive (ie: [924 930] will scrape from dates 924 to 930) (day 930 is the day you are predicting)
   
        
### Run sumPoints.py
    - Job: creates fanduel and draftkings pts based off performance
    - Updates futures to include fandue and draftkings points for previous day

### Scrape FanDuel -> generate features for current people
    - Job: put current players playing in the performance table
    - Pull in the FanDuel file that you are scraping from the competition you are entering
    - Split the first column into two columns and delimit by the dash (-)
    - Save and specify the location of the file in constants.py

### Run fanduelIDManagement.py
    - Job: put fanduel ID's in their place
    - Will tell if you do not have an id for a player

### Run fanduelScraper.py
    - Job: put players in their place like Roger Goodell would want to

### Run dailyMinutesScraper.py
    - Job: get minutes from rotogrinders and insert into performance table 
    - How: set minutesDateID to the dateID where you are projecting in constants.py

### Run projMinutes.sql
    - Job: projects the minutes for the people playing and don't have projMinutes
    - Gets the average minutes for a player over the last 7 days 

### Run currentMagic.py
    - Job: aggregates data from all tables and stores in "futures" table as features including everything just scraped
    	- only adds data of players whose projected minutes is not null for that day
    - Configure gdStartYear, gdStartMonth, gdStartDay to the date you want to pull features in up till  
    - set numdaysGradientDescent to how many days back you want to pull features till
    - these numbers are inclusive...

## Run train.py 
    - Must specify YearP, MonthP, and DayP for the day you are predicting
    - Uses the data in futures to train the models to everything up until that date 

### Run projMagic.py
    - Job: predict player performances using past data and ridge regression
    - Must specify YearP, MonthP, and DayP for the day you are predicting
    - Note the regression coefficents are stored in a file

### Run optimizer.py
    - Job: generate FanDuel lineups

## Regression Management
    - Goal: To efficently calculate the regression coefficents on our training set so that variance and bias is
    balanced
    - Right now, have two models - Ben Simmons Model and Lonzo Ball Model 
    - coefBen.npz cooresponds to Ben Simmons and is generated by train
    - coefLonzo.npz cooresponds to Lonzo and is generated by train 
    - used variations of a forward step wise feature selection method to generate features 


