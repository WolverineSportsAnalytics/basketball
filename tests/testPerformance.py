#End-to-end tests for NBA Performance Scraper (scraper that gets every player's individual stats for the day)

#Testing on OKC/ LAL game, Feb 8th, 2018
#www.basketball-reference.com/boxscores/201802080LAL.html

#And WAS/BOS game on the same day
#www.basketball-reference.com/boxscores/201802080WAS.html

import unittest

import mysql.connector

from datetime import timedelta, date

from bs4 import BeautifulSoup, Comment

import requests

import datetime as dt

import performance


class TestPerformanceMethods(unittest.TestCase):

    cnx = mysql.connector.connect(user="root",
            host="127.0.0.1",
            database="basketball",
            password="Federer123!")                                                                                                               

    
    cursor = cnx.cursor()

    def test_getDate(self):
        cnx = mysql.connector.connect(user="root",
            host="127.0.0.1",
            database="basketball",
            password="Federer123!")                                                                                                               

    
        cursor = cnx.cursor()
        day=25;
        month=10;
        year=2016;
        #test first and last column of new_dates
        self.assertEqual(performance.getDate(25, 10, 2016, cursor), 681);
        self.assertEqual(performance.getDate(27, 7, 2018, cursor), 1167);

    
    def test_getURLs(self):
         cnx = mysql.connector.connect(user="root",
            host="127.0.0.1",
            database="basketball",
            password="Federer123!")                                                                                                               

    
         cursor = cnx.cursor()
         startYear=2016;
         startMonth=10;
         startDay=25;

         endYear=2016;
         endMonth=10;
         endDay=31;

         my_urls=performance.getURLs(startDay, startMonth, startYear, endDay, endMonth, endYear, cursor)
         start_id=681
         end_id=687

         #test first and last URLs 
         self.assertEqual(my_urls[0][1], 'https://www.basketball-reference.com/boxscores/201610250CLE.html')
         self.assertEqual(my_urls[len(my_urls)-1][1], 'https://www.basketball-reference.com/boxscores/201610310TOR.html')

    def test_getPlayerID(self):
        cnx = mysql.connector.connect(user="root",
            host="127.0.0.1",
            database="basketball",
            password="Federer123!")                                                                                                               

    
        cursor = cnx.cursor()
        #test first player
        bbref_id = 'jokicni01';
        player_id= performance.getPlayerID(bbref_id, cursor)
        self.assertEqual(player_id, 1584)

        #test last player
        bbref_id='brookma01'
        player_id= performance.getPlayerID(bbref_id, cursor)
        self.assertEqual(player_id, 2814)

   
    def test_getTeams(self):
        url = 'https://www.basketball-reference.com/boxscores/201802080LAL.html'
        teams = performance.getTeams(url)
        self.assertEqual(teams[0], 'OKC')
        self.assertEqual(teams[1], 'LAL')



    def test_updateAndInsertPlayerRef(self): #top-level scraper function
        
         cnx = mysql.connector.connect(user="root",
            host="127.0.0.1",
            database="basketball",
            password="Federer123!")                                                                                                               

    
         cursor = cnx.cursor()

         start_day = 8;
         start_month =2;
         start_year = 2018;
         performance.updateAndInsertPlayerRef(start_day, start_month, start_year, start_day, start_month, start_year, cursor, cnx)
         select = "SELECT * FROM performance WHERE dateID = 997"
         cursor.execute(select)
         result = cursor.fetchall()
         self.assertEqual(result[0][1], 1788) #first player of the day
         self.assertEqual(result[len(result)-1][1], 1744) #last player of the day
       
        


if __name__ == '__main__':
    unittest.main()
        

        
        
            
        
        

    
        
        














