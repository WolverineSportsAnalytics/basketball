from datetime import date
import mysql.connector
from pydfs_lineup_optimizer import *
import datetime

'''
Pulls in our projections and the sallarys of current players and optimizing for the night
Optimizes using pydfs_lineup_optimizer
'''


def getDate(day, month, year, cursor):
    findGame = 'SELECT iddates FROM new_dates WHERE date = %s'
    findGameData = (date(year, month, day),)
    cursor.execute(findGame, findGameData)

    dateID = -1
    for datez in cursor:
        dateID = datez[0]

    return dateID


def optimize(day, month, year, cursor):
    gameID = getDate(day, month, year, cursor)
    print gameID

    # get players
    playas = []
    dkPointsDict = {}
    dkPlayersPoints = {}

    getPlayersQuery = "SELECT b.nickName, p.playerID, p.fanduelPosition, p.leProj, p.team, p.fanduel, p.opponent, p.fanduelPts FROM basketball.performance as p LEFT JOIN basketball.player_reference as b ON b.playerID = p.playerID WHERE p.dateID = %s AND p.projMinutes >= 8 AND p.fanduel > 0 AND p.leProj IS NOT NULL AND p.leProj > 0"
    getBPlayersData = (gameID,)
    cursor.execute(getPlayersQuery, getBPlayersData)

    print ("Number of players being considered: " + str(cursor.rowcount))
    players = cursor.fetchall()

    for baller in players:
        positions = []
        positions.append(str(baller[2]))
        dkPointsDict[baller[1]] = float(baller[7])
        dkPlayersPoints[baller[1]] = baller[0]

        newPlaya = Player(baller[1], baller[0], "", positions, baller[4], int(baller[5]), float(baller[3]))
        playas.append(newPlaya)

    # instantiate optimizer + run

    C_optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    PF_optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    SF_optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    SG_optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    PG_optimizer = get_optimizer(Site.FANDUEL, Sport.BASKETBALL)
    C_optimizer.load_players(playas)
    PF_optimizer.load_players(playas)
    SF_optimizer.load_players(playas)
    SG_optimizer.load_players(playas)
    PG_optimizer.load_players(playas)
    
    # if duplicate player, increase n + generate next lineup,
    # next lineup will generate lineup with next highest amount of points
    numLineups = 1;
    names_to_hold = []
    lineups = []

    # hold a center with lowest salary, highest points
    Best_worst_C_pts = 0
    Best_worst_PG_pts = 0
    Best_worst_PF_pts = 0
    Best_worst_SG_pts = 0
    Best_worst_SF_pts = 0
    for playa in playas:
        if playa.salary == 3500:
            if playa.positions[0] == 'C':
                if playa.fppg > Best_worst_C_pts:
                    Best_worst_C_pts = playa.fppg
                    Best_worst_C = playa.first_name + playa.last_name
            elif playa.positions[0] == 'PG':
                if playa.fppg > Best_worst_PG_pts:
                    Best_worst_PG_pts = playa.fppg
                    Best_worst_PG = playa.first_name + playa.last_name
            elif playa.positions[0] == 'PF':
                if playa.fppg > Best_worst_PF_pts:
                    Best_worst_PF_pts = playa.fppg
                    Best_worst_PF = playa.first_name + playa.last_name
            elif playa.positions[0] == 'SG':
                if playa.fppg > Best_worst_SG_pts:
                    Best_worst_SG_pts = playa.fppg
                    Best_worst_SG = playa.first_name + playa.last_name
            elif playa.positions[0] == 'SF':
                if playa.fppg > Best_worst_SF_pts:
                    Best_worst_SF_pts = playa.fppg
                    Best_worst_SF = playa.first_name + playa.last_name

    # create list with all above generated names - done
    # create linup(s) for each point in list, which will be for each 'held' player
    
    specific_playa = C_optimizer.get_player_by_name(Best_worst_C)
    C_optimizer.add_player_to_lineup(specific_playa)
    lineups.append(C_optimizer.optimize(n=numLineups))

    specific_playa = PF_optimizer.get_player_by_name(Best_worst_PF)
    PF_optimizer.add_player_to_lineup(specific_playa)
    lineups.append(PF_optimizer.optimize(n=numLineups))

    specific_playa = SF_optimizer.get_player_by_name(Best_worst_SF)
    SF_optimizer.add_player_to_lineup(specific_playa)
    lineups.append(SF_optimizer.optimize(n=numLineups))

    specific_playa = SG_optimizer.get_player_by_name(Best_worst_SG)
    SG_optimizer.add_player_to_lineup(specific_playa)
    lineups.append(SG_optimizer.optimize(n=numLineups))
    
    specific_playa = PG_optimizer.get_player_by_name(Best_worst_PG)
    PG_optimizer.add_player_to_lineup(specific_playa)
    lineups.append(PG_optimizer.optimize(n=numLineups))
    
    #optimizer.remove_player_from_lineup(specific_playa)

    '''
    Take these lineups and insert into database
    follow from WNBA
 
    Start without slate first
    '''
    for generator in lineups:
        for lineup in generator:
            print(lineup)
            print(lineup.fantasy_points_projection)
            print(lineup.salary_costs)

            playerIDList = []
            dkpoints = 0
            for player in lineup.lineup:
                playerIDList.append(player.id)

            for player in playerIDList:
                dkpoints = dkpoints + dkPointsDict[player]
                playerName = dkPlayersPoints[player]

                # print optimized lineups
                print("Player Name: " + str(playerName) + "; Actual Points Scored: " + str(dkPointsDict[player]))

            print("Total Points: " + str(dkpoints))
            print ("\n")


if __name__ == "__main__":
    cnx = mysql.connector.connect(user="wsa@wsabasketball",
                                  host='wsabasketball.mysql.database.azure.com',
                                  database="basketball",
                                  password="LeBron>MJ!")
    cursor = cnx.cursor(buffered=True)


    day = 6
    year = 2019
    month = 4


    optimize(day, month, year, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()


