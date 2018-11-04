''' Extropilate team performances to keep a running average '''

''' Model this off of https://github.com/WolverineSportsAnalytics/basketball/blob/master/teamPerformanceExtrapolation.py '''
def get_data_from_performance(cnx, cursor, first_date, last_date):
    ''' 
    This gets data from the teamPerformance table 
    so will get a cetain number of individual  performances for all teams
    In between first date and last date these are dateID's
    '''
    performances = []
    return performances

def average_data(performances):
    ''' Averages data over all performances 
    Takes a list of performances for all teams and averages over them
    '''
    
    averages = []
    return averages

def insert_into_dailyPerformance(cnx, cursor, averages):
    ''' Inserts into the teamPerformance table '''
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
