from bs4 import BeautifulSoup
import urllib2
import csv
import demjson

def rotogrinders_season_scraper():
	url = "https://rotogrinders.com/game-stats/nba-player?site=fanduel&range=season"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_season_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrinders_fourweeks_scraper():
	url = "https://rotogrinders.com/game-stats/nba-player?site=fanduel&range=4weeks"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_fourweeks_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrinders_minutes_scraper():
	url = "https://rotogrinders.com/projected-stats/nba-player"
	stats = ["Player", "Team", "Pos", "Salary", "GP", "Min", "Reb", "Ast", "Stl", "Blk", "TO", "Pts", "USG", "FPTS"]
	csv_filename = 'rotogrinders_minutes_basketball.csv'
	rotogrindersBasketball(url, csv_filename, stats)

def rotogrindersBasketball(url, csv_filename, stats):
	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page, "html.parser")

	file = open(csv_filename, 'w')
	for stat in stats:
		file.write(stat + ", ")
	file.write("\n")

	jsonData = soup.find_all('script')
	jsonData = jsonData[len(jsonData) -1]

	jsonData = jsonData.text

	junk,jsonData = jsonData.split("data =")
	jsonData = jsonData.lstrip()
	jsonData = jsonData.rstrip()

	jsonData = jsonData.split(";")
	jsonData = jsonData[0]

#	jsonData = jsonData[:-1]

	basketballData = demjson.decode(jsonData)

	for playerData in basketballData:
		print playerData
		name = playerData['player']['first_name']
		print name
		print playerData['minutes']
		team = playerData['team']
		pos = playerData['pos']
		salary = playerData['salary']
		gp = playerData['gp']
		mins = float(playerData['min']) / float(gp)
		reb = float(playerData['reb']) / float(gp)
		ast = float(playerData['ast']) / float(gp)
		stl = float(playerData['stl']) / float(gp)
		blk = float(playerData['blk']) / float(gp)
		to = float(playerData['to']) / float(gp)
		pts = float(playerData['pts']) / float(gp)
		usg = playerData['usg']
		fpts = playerData['fpts']
		fpts = float(fpts) / float(gp)
		fpts = round(fpts, 2)

		data = (player, team, pos, salary, gp, mins, reb, ast, stl, blk, to, pts, usg, fpts)
		file.write('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s \n' % data)

	file.close()


if __name__ == "__main__":
	rotogrinders_minutes_scraper()
