import mysql.connector
import requests
from bs4 import BeautifulSoup
# import constants

team_abrev = ["ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

def generateURLS():
    urls = []
    for team in team_abrev:
        urls.append(("https://www.basketball-reference.com/teams/" + team + "/2019.html", team))

    return urls


class PlayerRefObject:

    def __init__(self, name, team, bbrefID):
        self.name = name
        self.team = team
        self.bbrefID = bbrefID

    def add_to_table(self, cursor, cnx):
        addPlayer = "INSERT INTO player_reference (nickName, bbrefID, firstName, lastName, team) VALUES(%s, %s, %s, %s, %s)"
        payload = (self.name, self.bbrefID, self.name.split()[0], " ".join(self.name.split()[1:]), self.team)

        cursor.execute(addPlayer, payload)
        cnx.commit()


def scrapeHtml(cursor, cnx):
    urls = generateURLS()
    findPlayer = "SELECT bbrefID FROM player_reference WHERE bbrefID = %s"
    updatePlayer = "UPDATE player_reference SET team = %s WHERE bbrefID = %s"

    for url in urls:
        page = requests.get(url[0])
        soup = BeautifulSoup(page.text, 'html.parser')

	try:
          tables = soup.find_all("table")
          players_table = tables[0]
          rows = players_table.find_all("tr")

          for tr in rows[1:]:
            row = tr.find_all("td")[0]
            bbref = row.a['href'].split("/")[-1].split(".")[0]
            name = row.a.text
            team = url[1]

            findPlayerQ = (bbref,)
            cursor.execute(findPlayer, findPlayerQ)

	    exists = cursor.fetchall() # get players 

            if not exists:
                # add because did not find anything
                player = PlayerRefObject(name, team, bbref)
                player.add_to_table(cursor, cnx)
            else:
                # update
                updatePQ = (team, bbref)
                cursor.execute(updatePlayer, updatePQ) 
	except Exception as e:
		print(e, url)
		

if __name__ == "__main__":
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)
    scrapeHtml(cursor, cnx)
