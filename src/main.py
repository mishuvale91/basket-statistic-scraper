#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main file
"""
Created on Mon Oct 26 18:16:11 2020

@author: Juan Penalta Rodríguez y Michaelle Valenzuela Sangoquiza
"""
import Utils as utils
from LeagueScraperFactory import ScraperFactory


logger = utils.getLogger('basketScraper')
args = utils.getArgs()

# get commandline args
logger.info("Get args from command line")
leagues = args.league
start_season = int(args.startSeason)
end_season = int(args.endSeason)

# get csv filePath.
file_path = utils.getfilePaht(leagues, start_season, end_season)
logger.info('Create file {0}'.format(file_path))

# write header to csv file.
utils.writeToCSV(file_path, [ utils.HEADER_LIST ])

#   Extract data for leagues
for league in leagues.split('-'): 

    logger.info('Get players from {0} between season {1} and season {2}'
                    .format(league, start_season, end_season))    
    if( start_season <= end_season):
        
        # get scraper instance for the league
        logger.info('Get instance for {0} league'. format(league))
        scraperFactory= ScraperFactory(logger)
        league = scraperFactory.getInstance(league)
          
        for season in range(start_season, end_season+1):
            logger.info("Get season {0}".format(season)) 
            player_list = league.getSeasonPlayers(season)
            # write data to csv file
            utils.writeToCSV(file_path, player_list)
                  
    else:
        print("starSeason must be lower or equal than endSeason")
    