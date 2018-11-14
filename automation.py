#!/usr/bin/python3
''' Automate of running WSA Engine '''
import mysql.connector
import datetime
import teamPerformance

def main():
    ''' Script to automate running of all basketball engine daily '''
    run_scrapers()

def run_scrapers():
    ''' Run the scrapers '''
    cursor = _
    cnx = _
    dateID = _
    today = _

    # run player reference scaper

    # run generate box score urls

    # run performance 

    # run team performance
    teamPerformance.statsFiller(today.day, today.month, today.year, today.day, today.month, today.year, cnx, cursor)
    # 3 Extrapilators

    # fandual scraper 

    # daily minutes

    # machine learning stuff

    pass
