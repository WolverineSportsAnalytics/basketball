import mysql.connector
from datetime import timedelta, date
import constants
from bs4 import BeautifulSoup, Comment
import urllib2
import requests
import csv
def fd_pos_convert(pos):
	if pos == '1':
		return 'PG'
	if pos == '2':
		return 'SG'
	if pos == '3':
		return 'SF'
	if pos == '4':
		return 'PF'
	if pos == '5':
		return 'C'

def dk_pos_convert(pos):
	if len(pos) == 1:
		return fd_pos_convert(pos)
	elif len(pos) == 2:
		return fd_pos_convert(pos[0]) + '/' + fd_pos_convert(pos[1])

def date_convert(date):
	return date[:4] + "-" + date[4:6] + "-" + date[6:8]


def scrape_rotoguru(cursor, cnx):
	#empty will be used to scrape from rotoguru csv
    	selec_id = "select playerID from player_reference where nickName=\""
    	selec_date_id = "select iddates from new_dates where date=\""
 
 	update_performance = "Update performance set fanduel=%s, draftkings=%s, fanduelPosition=%s, draftkingsPosition=%s where playerID=%s and dateID=%s"  
	false = []
	with open('rotoguru20162017data.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		i = 0
		for row in reader:
			try:
				name = row[3]
				print name
                	    	get_id = selec_id + name + "\""
                	    	cursor.execute(get_id)
                	    	player_id = cursor.fetchall()[0][0]
				print player_id


				date = row[4]
				print date_convert(date)
				get_date = selec_date_id + date + "\""
                	    	cursor.execute(get_date)
                	    	date_id = cursor.fetchall()[0][0]
				print date_id	


				dk_salary = row[25] 
				print dk_salary
				fd_salary = row[23]
				print fd_salary
				dk_pos = row[32]
				dk_pos = dk_pos_convert(dk_pos)
				fd_pos = row[31]
				fd_pos = fd_pos_convert(fd_pos)
				print fd_pos

				inserts = (
						fd_salary,
						dk_salary,
						fd_pos,
						dk_pos,
						player_id,
						date_id)
			
				
				cursor.execute(update_performance,inserts)	

			except:
				false.append(name)


	cursor.close()
        cnx.commit()
        cnx.close()


	for i in false:
		print i


if __name__ == "__main__":
    cnx = mysql.connector.connect(user=constants.databaseUser,
                                  host=constants.databaseHost,
                                  database=constants.databaseName,
                                  password=constants.databasePassword)
    cursor = cnx.cursor(buffered=True)

    scrape_rotoguru(cursor, cnx)
