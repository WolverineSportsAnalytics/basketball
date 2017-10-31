import re
import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests


def updateAndInsertPlayerRef(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor):
    
    # set range of dates	
    #urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    urls = ["https://www.basketball-reference.com/boxscores/201704070DAL.html"]
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)

    insert_team_data = "INSERT INTO basketball.team_performance (dailyTeamID, dailyTeamOpponentID, dateID, pointsAllowed, pointsScored, pace, effectiveFieldGoalPercent, turnoverPercent, FT/FGA, offensiveRating, defensiveRating, FG, FGA, FGP, 3P, 3PA, 3PP, FT, FTA, FTP, offensiveRebounds, defensiveRebounds, totalebounds, assists, steal, blocks, turnovers, personalFouls, trueShootingPercent, 3pointAttemptRate, freeThrowAttemptRate, defensiveReboundPercent, offensiveReboundPercent, totalReboundPercent, assistPercent, stealPercent, blockPercent) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"




	
    # loop through all url's 
    for url in urls:
	page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
	
	soup.findAll(text=lambda text:isinstance(text, Comment))
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	comment = comments[len(comments) - 23]

        teams_data = [[],[]]
	soup1 = BeautifulSoup(comment, "html.parser")
        team_num = 0

	for tr in soup1.find_all('tr')[2:]:
		
		#team name
		team = tr.find_all('th')[0].text
	
		#table columns

		tds = tr.find_all('td')
		pace = tds[0].text
		eShooting = tds[1].text
		turnoverPercent = tds[2].text
		oReboundPercent = tds[3].text
		FTOverFQAttempts = tds[4].text
		ORTG = tds[5].text
                
                teams_data[team_num].append(team)
                teams_data[team_num].append(pace)
                teams_data[team_num].append(eShooting)
                teams_data[team_num].append(turnoverPercent)
                teams_data[team_num].append(oReboundPercent)
                teams_data[team_num].append(FTOverFQAttempts)
                teams_data[team_num].append(ORTG)
                team_num=+1
                

	
	team_num = 0
        for tfoot in soup.find_all('tfoot'):
            td = tfoot.find_all('td')
            for i in td:
                teams_data[team_num/2].append(i.text)
            team_num+=1

        teams_data[0].append(teams_data[1][0])
        teams_data[1].append(teams_data[0][0])

        selec_id = "select teamID from team_reference where bbreff=\""
        get_team = selec_id + teams_data[0][0] + "\""
        cursor.execute(get_team)
        h_team_id = cursor.fetchall()[0][0]
        
        get_team = selec_id + teams_data[1][0] + "\""
        cursor.execute(get_team)
        a_team_id = cursor.fetchall()[0][0]

        teams_data[0][0] = h_team_id
        teams_data[0][len(teams_data[0]) - 1] = a_team_id
        teams_data[1][0] = a_team_id
        teams_data[1][len(teams_data[0]) - 1] = h_team_id
        for team in teams_data:
            
            print team

if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    updateAndInsertPlayerRef(constants.startDayP, constants.startMonthP, constants.startYearP, constants.endDayP, constants.endMonthP, constants.endYearP, cursor )


    cursor.close()
    cnx.commit()
    cnx.close()
