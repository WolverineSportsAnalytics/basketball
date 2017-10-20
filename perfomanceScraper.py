import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear):
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
    urls = []
    for single_date in daterange(start_date, end_date):
        urls.append('https://www.basketball-reference.com/friv/dailyleaders.fcgi?month=' + str(single_date.month) +
                    '&day=' + str(single_date.day) + '&year=' + str(single_date.year))
    return urls

def updateAndInsertPlayerRef(startDay, startMonth, startYear, endDay, endMonth, endYear,cursor,cnx ):
    
    # set range of dates	
    # urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)


    select_dates = "Select * from box_score_urls;"
    cursor.execute(select_dates)
    box_url = cursor.fetchall()
    url = []

    cursor.close()
    cnx.commit()
    cnx.close()


    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
   
    dates = []
    for single_date in daterange(start_date, end_date):
	    dates.append(str(single_date.year) + '-' + str(single_date.month) + '-' + str(single_date.day))
	

    selec_id = "select playerID from player_reference where nickName=\"" 
    date_counter = 0
    
    # loop through all url's 
    for score in box_url:
    	cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
	cursor = cnx.cursor(buffered=True)
   
	url = score[1]    
	#print get_date
	page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
	soup.findAll(text=lambda text:isinstance(text, Comment))
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	
	comment = comments[len(comments)-24]
	soup1 = BeautifulSoup(comment, "html.parser")

	teams=[]
	for i in soup1.find_all('tr')[2:]:
		l = i.find_all("td")[0].text
		teams.append(l)
	date_id = score[2] 

	tables = soup.find_all("tbody")
        
	team_tables = [[tables[0],tables[1], teams[0],teams[1], 0],[tables[2],tables[3],teams[1],teams[0],1]]

	for team in team_tables:
		# set team specific data
		tea = team[2]
		opp = team[3]
		rows_1 = team[0].find_all('tr')
		rows_2 = team[1].find_all('tr')
		home = team[4]
		# scrape regular stats
		for number in range(len(rows_1)):
	            # first find, then updated
	        	try:
		                nickName = rows_1[number].find_all('th')[0].a.text
	     	 		tds1 = rows_1[number].find_all('td')
	                	minutes = tds1[0].text
				get_id = selec_id + nickName  + "\""
				cursor.execute(get_id)
				player_id = cursor.fetchall()[0][0]
	                	blocks = tds1[15].text
				steals = tds1[14].text
				points = tds1[18].text
				assists = tds1[13].text
				to = tds1[16].text
				rebounds = tds1[12].text
		 		triple_double = 0
				double_double = 0
				o_rebs = tds1[10].text
				d_rebs = tds1[11].text
				
				fgs = tds1[1].text
                        	fga = tds1[2].text
				if fga == 0:
					fgpercent = "NULL"
				else:
					fgpercent = tds1[3].text

				 	
				tpm = tds1[4].text
				tpa = tds1[5].text
				if tpa ==0:
					 tp_percent = "NULL"
				else:
					 tp_percent = tds1[6].text

				free_throws = tds1[7].text
				fta = tds1[8].text
				if fta == 0:
				 	ft_percent = "NULL"
				else:
					ft_percent = tds1[9].text

				pf = tds1[17].text
				plus_minus = tds1[19].text

				# advanced statistics 
				tds = rows_2[number].find_all('td')
				TS = tds[1].text
				eFG = tds[2].text
				TPAR = tds[3].text
				FTR= tds[4].text
				ORBR= tds[5].text
				DRBR= tds[6].text
				TRBR= tds[7].text
				ASTR= tds[8].text
				STLR= tds[9].text
				BLKR= tds[10].text
				TOVR= tds[11].text
				USGR= tds[12].text
				ORtg= tds[13].text
				DRtg = tds[14].text	

				plus_tens = 0
				if int(steals) >= 10:
					plus_tens += 1
				if int(blocks) >= 10:
					plus_tens += 1
				if int(points) >= 10:	
					plus_tens += 1
				if int(assists) >= 10:
					plus_tens += 1
				if int(rebounds) >= 10:
					plus_tens += 1
	
				if plus_tens > 2:
					triple_double = 1
				elif plus_tens > 1:
					double_double = 1


				inserts = (player_id, date_id, points, minutes, fgs, fga, fgpercent, tpm, tpa, tp_percent, free_throws, fta, ft_percent, o_rebs, d_rebs, rebounds, assists, steals, blocks, to, pf, plus_minus, TS, eFG, TPAR, FTR, ORBR, DRBR, TRBR, ASTR, STLR, BLKR, TOVR, USGR, ORtg, DRtg, triple_double, double_double, tea, opp, home)
	
		        	update_performance = "INSERT INTO performance (playerID, dateID, points, minutesPlayed, fieldGoals, fieldGoalsAttempted, fieldGoalPercent, 3PM, 3PA, 3PPercent, FT, FTA, FTPercent, offensiveRebounds, defensiveRebounds, totalRebounds, assists,  steals, blocks, turnovers, personalFouls, plusMinus, trueShootingPercent, effectiveFieldGoalPercent, 3pointAttemptRate, freeThrowAttemptRate, offensiveReboundPercent, defensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent, turnoverPercent, usagePercent, offensiveRating, defensiveRating,  tripleDouble, doubleDouble, team, opponent, home) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		
				cursor.execute(update_performance, inserts)	
			
					
					
			except:
				pass
	cursor.close()
    	cnx.commit()
    	cnx.close()

if __name__ == "__main__":
	cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
	cursor = cnx.cursor(buffered=True)

	updateAndInsertPlayerRef(constants.startDayP, constants.startMonthP, constants.startYearP, constants.endDayP, constants.endMonthP, constants.endYearP,cursor,cnx)



  
