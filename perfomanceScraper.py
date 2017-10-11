import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup
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


def updateAndInsertPlayerRef(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor):
    
    # set range of dates	
    urls = generateURLs(startDay, startMonth, startYear, endDay, endMonth, endYear)
    start_date = date(startYear, startMonth, startDay)
    end_date = date(endYear, endMonth, endDay)
   
    dates = []
    for single_date in daterange(start_date, end_date):
	    dates.append(str(single_date.year) + '-' + str(single_date.month) + '-' + str(single_date.day))
	

    select_date = "select iddates from new_dates where date = \""
    selec_id = "select playerID from player_reference where nickName=\"" 
    date_counter = 0
    
    # loop through all url's 
    for url in urls:
	get_date = select_date + dates[date_counter] + "\""
        print get_date
	page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        update_performance = "INSERT INTO performance (playerID, dateID, blocks, steals, points, assists, turnovers, 3PM, rebounds, doubleDouble, tripleDouble) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	cursor.execute(get_date)
	date_id = cursor.fetchall()[0][0]
	print date_id


        for tr in soup.find_all('tr')[1:]:
            # first find, then updated
            try:
                tds = tr.find_all('td')
                nickName = tds[0].a.text
		get_id = selec_id + nickName  + "\""
		cursor.execute(get_id)
		player_id = cursor.fetchall()[0][0]
	
                blocks = tds[20].text
		steals = tds[19].text
		points = tds[23].text
		assists = tds[18].text
		to = tds[21].text
		tpm = tds[10].text
		rebounds = tds[17].text
		triple_double = 0
		double_double = 0


		plus_tens = 0
		if int(steals) > 10:
			plus_tens += 1
		if int(blocks) > 10:
			plus_tens += 1
		if int(points) > 10:	
			plus_tens += 1
		if int(assists) > 10:
			plus_tens += 1
		if int(rebounds) > 10:
			plus_tens += 1

		if plus_tens > 2:
			triple_double = 1
		elif plus_tens > 1:
			double_double = 1
		
		inserts = (player_id, date_id, blocks,steals, points, assists, to, tpm , rebounds, triple_double, double_double)
		cursor.execute(update_performance, inserts)
            except:
		    pass

	date_counter+=1 


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
