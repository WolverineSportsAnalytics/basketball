from bs4 import BeautifulSoup, Comment
import mysql.connector
import requests
import datetime

def get_player_id(f_name, l_name, pos, team, cursor):

    ''' will get player id if nickname doesn't match will use first name + team
    then last name + team then first part of last name + team name '''

    getPlayerID = "select playerID from player_reference where nickName = %s"
    inserts = (f_name + " " + l_name,)
    cursor.execute(getPlayerID, inserts)
    if cursor.rowcount != 0:
        return cursor.fetchall()[0][0]

    getPlayerByTeam = "select playerID from player_reference where lastName= %s and team = %s"
    inserts = (l_name, team)
    cursor.execute(getPlayerByTeam, inserts)
    if cursor.rowcount != 0:
        return cursor.fetchall()[0][0]

    getPlayerByTeam = "select playerID from player_reference where firstName=%s and team = %s"
    inserts = (f_name, team)
    cursor.execute(getPlayerByTeam, inserts)
    if cursor.rowcount != 0:
        return cursor.fetchall()[0][0]

    getPlayerByTeam = "select playerID from player_reference where lastName= %s and team = %s"
    inserts = (l_name.split()[0], team)
    cursor.execute(getPlayerByTeam, inserts)
    if cursor.rowcount != 0:
        return cursor.fetchall()[0][0]

    return " "


def insert_into_performance(cursor, cnx, dateID, url):
    update_performance = "Update performance set fanduel=%s, team=%s, opponent=%s, fanduelPosition=%s where playerID=%s and dateID=%s"

    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')
    for row in soup.find_all("tr"):
        data = row.find_all("td")
        try:
            pos= data[0].text
            last_name, first_name = data[1].text.split(",")
            salary = data[3].text
            salary = salary[1:]
            salary = str("".join(salary.split(",")))
            team = data[4].text.upper()
            opp = data[5].text.split()[1].upper()
            if pos == "NA" or pos.split()[0] == "Jump":
                continue

	    if team == "CHA":
            	    team = "CHO"
            if team == "BKN":
            	    team = "BRK"
	    if opp == "CHA":
            	opp = "CHO"
            if opp == "BKN":
            	opp = "BRK"
        except:
            continue
        
        try:
            if first_name[-1] == '^':
                first_name = first_name[:-1]
            first_name = first_name.strip()
            name = first_name + " " + last_name
            player_id = get_player_id(first_name, last_name, pos, team, cursor)


            inserts = (salary, team, opp, pos, player_id, dateID)
	    cursor.execute(update_performance, inserts)
            cnx.commit()
        except Exception as E:
            print(E)
    

def get_urls_in_range(dates):
    ''' takes in list of date objects and returns urls '''
    urls = []
    for date in dates:
        url = "http://rotoguru1.com/cgi-bin/hyday.pl?mon=" + str(date.month)  +"&day=" + str(date.day) + "&year="+ str(date.year) + "&game=fd"
        urls.append(url)

    return urls

def getDate(date, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (datetime.date(date.year, date.month, date.day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID

def get_date_ids(date_list, cursor):
    dates = []
    for date in date_list:
        dates.append(getDate(date, cursor))
    return dates
    
def run_scraper_from_today(cursor, cnx, numdays):
    ''' Will run this scraper to insert into the perfomance table starting from todays date with the number of days you need to go back '''

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
    urls = get_urls_in_range(date_list)

    dateIDs = get_date_ids(date_list, cursor)
    
    for i in range(numdays):
        print(dateIDs[i])
        insert_into_performance(cursor,cnx, dateIDs[i], urls[i])


if __name__=="__main__":
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="")
    cursor = cnx.cursor(buffered=True)
    run_scraper_from_today(cursor,cnx, 20)
