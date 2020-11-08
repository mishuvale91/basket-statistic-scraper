#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 08:03:57 2020

@author: Juan Penalta Rodríguez y Michaelle Valenzuela Sangoquiza
"""
from ACBStatisticsScraper import ACBScraper
from LegaStatisticsScraper import LegaScraper

ACB = "acb"
LEGA = "lega"

class ScraperFactory:
    
    def __init__(self, logger):
        self.logger = logger
        
    #   Return a instace for a leagueScraper.    
    def getInstance(self, league):
        
        factory = None
        
        if league == ACB: 
            factory = ACBScraper()
        elif league == LEGA:
            factory = LegaScraper()
        else: 
            self.logger.error("The factory not exists, valid factorys are: acb, lega")
               
        return factory
