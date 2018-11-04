''' Extropilate Daily performance to keep a running average '''

''' Model this off of https://github.com/WolverineSportsAnalytics/basketball/blob/master/dailyPerformanceExtrapolation.py '''
def get_data_from_performance(cnx, cursor, first_date, last_date):
    ''' 
    This gets data from the performance table 
    so will get a cetain number of individual performances for all player 
    In between first data and last data
    '''
    performances = []
    return performances

def average_data(performances):
    ''' Averages data over all performances 
    Takes a list of performances for all players and averages over them
    '''
    
    averages = []
    return averages

def insert_into_dailyPerformance(cnx, cursor, averages):
    ''' Inserts into the dailyPerformance table '''
    # test this by inserting into local database
    pass

def main():
    cnx_wsa = mysql.connector.connect(user="wsabasketball.mysql.database.azure.com",
                                  host="wsa@wsabasketball",
                                  database="basketball",
                                  password="" ) # fill in password here)
    cursor_wsa = cnx.cursor(buffered=True)

    performances = get_data_from_performance(cnx_wsa, cursor_wsa, first_date, last_date)
    averages = average_data(performances)

    cnx_local = mysql.connector.connect(user="root",
                                  host='127.0.0.1',
                                  database="basketball",
                                  password="")
    cursor_local = cnx.cursor(buffered=True)

    insert_into_dailyPerformance(cnx_local, cursor_loca, averages)
