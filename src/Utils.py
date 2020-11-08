#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Utils methods
"""
Created on Fri Nov  6 19:54:24 2020

@author: Juan Penalta Rodríguez y Michaelle Valenzuela Sangoquiza
"""

import logging
import os
import csv
import argparse
import requests
import time


HEADER_LIST = ['league','game_date','local_team','local_team_points'
               ,'visit_team','visit_team_points'
               ,'player_team','player_name','player_total_points','time'
               ,'one_point_shots_get','one_point_shots_made'
               ,'two_point_shots_get','two_point_shots_made'
               ,'three_point_shots_get','three_point_shots_made'
               ,'rebouts','assists','fouls','received_fouls']

FILE_PATTER = "players_{0}_{1}_{2}.csv"
MAX_RESPONSE_TIME = 0.5
DELAY_MULT = 5

#   Return the command line args.
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--startSeason", help="Enter start season of interval")
    parser.add_argument("--endSeason", help="Enter end season of interval")
    parser.add_argument("--league", help="Enter league: acb, lega")
    args = parser.parse_args()
    return args

#   Return a instance of the console logger
def getLogger(logger_name):
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    
    return logger

# Return the csv file path
def getfilePaht(league, start_season, end_season):
    current_dir = os.path.dirname(__file__)
    filename = FILE_PATTER.format(league, start_season, end_season)
    return os.path.join(current_dir, filename)
        
#   Append lines to a csv file
def writeToCSV(file_path, player_list):
    with open(file_path, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for player in player_list:
            writer.writerow(player)
  
#   Do a get request to a url and return the response
def getRequest(url, logger):
    start_time = time.time()
    
    response = requests.get(url)
    
    response_delay = time.time() - start_time
    if response_delay > MAX_RESPONSE_TIME:
        delay = DELAY_MULT * response_delay
        logger.info("Delay response time: {0}, sleep for: {1} ".format(response_delay, delay))
        time.sleep(delay)
    
    return response

