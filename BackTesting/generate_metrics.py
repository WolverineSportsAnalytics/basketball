import mysql.connector

models = ["mlp", "ridge"]
projection_type = ["lower", "regular", "upper"]
optimizer_type = ["regular", "low_salary"]


def get_average(cursor, cnx):
    base_string = "select avg(actualPointsLineup)  FROM basketball.historic_lineups where model like '{0}_';"
    for model in models:
        get_avg = base_string.format(model)

        cursor.execute(get_avg)

        average = cursor.fetchall()[0][0]
        print model, average
        # insert into new table when we make it

def get_median(cursor, cnx):
    base_string = "select actualPointsLineup FROM basketball.historic_lineups where model like '{0}_' order by actualPointsLineup;"
    base_count = "select count(*) FROM basketball.historic_lineups where model like '{0}_';"
    for model in models:
        get_avg = base_string.format(model)
        get_count = base_count.format(model)

        cursor.execute(get_count)
        median_index = cursor.fetchall()[0][0]
        if median_index % 2 == 0:
            median_index = median_index/2
        else: 
            median_index  = (median_index-1)/2

        cursor.execute(get_avg)

        actualPoints = cursor.fetchall()
        median = actualPoints[median_index][0]

        print model, median
            
        # insert into new table when we make it
 
def get_win_percentages(cursor, cnx):
    base_count = "select count(*) FROM basketball.historic_lineups where model like '{0}_';"
    base_count_greater = "select count(*) FROM basketball.historic_lineups where model like '{0}_' and actualPointsLineup > {1};"
    win_numbers = [290,300,310,320]
    for model in models:
        get_count = base_count.format(model)
        cursor.execute(get_count)
        total_count= cursor.fetchall()[0][0]
        for win in win_numbers:
            get_count_greater = base_count_greater.format(model, win)
            cursor.execute(get_count_greater)
            numGreater = cursor.fetchall()[0][0]
            print model, win, numGreater/float(total_count)
            

def get_metrics():
    cnx = mysql.connector.connect(user="wsa",
                                  host='34.68.250.121',
                                  database="basketball",
                                  password=password)
    cursor = cnx.cursor(buffered=True)

    get_average(cursor, cnx)
    get_median(cursor, cnx)
    get_win_percentages(cursor, cnx)


if __name__=="__main__":
    get_metrics()


