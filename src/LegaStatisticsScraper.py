#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 14:59:20 2020

@author: Juan Penalta Rodríguez y Michaelle Valenzuela Sangoquiza
"""

from bs4 import BeautifulSoup
import Utils as utils


PLAYER_NAME_FIELD = 2
TOTAL_POINTS_FIELD = 3
TIME_FIELD = 4
SHOT1_FIELD = 14
SHOT1_MAKE_FIELD = 15
SHOT2_FIELD = 7
SHOT2_MAKE_FIELD = 8
SHOT3_FIELD = 11
SHOT3_MAKE_FIELD = 12
REBOUTS_FIELD = 19
ASSISTS_FIELD = 24
FOULS_FIELD = 5
FOULS_RECEIVED_FIELD = 6
LEGA_NAME = 'lega'

GAME_STATISTICS_URL = 'http://web.legabasket.it/game/{0}/' 
GAMES_URL = 'http://web.legabasket.it/team/tbd.phtml?club={0}&type=d1&from={1}&j1=0&j2=0&t=3'
SEASON_TEAMS_URL ='http://web.legabasket.it/team/tbd.phtml?club={0}&type=d1&from=2020&j1=0&j2=0&t=3'



class LegaScraper:
    def __init__(self):
        self.logger = utils.getLogger('LegaScraper')

    #   Check if it is a row that contains player data.        
    def isPlayer(self, row):
        return row!= None and row[PLAYER_NAME_FIELD].text != 'Totali' and row[PLAYER_NAME_FIELD].text != 'Squadra'

    #   Check if the value is a not valid data.       
    def isEmptyField(self, value):
        return value == None
    
    #   Return the value of the column if it is a valid value or a empty string
    #   in other case.
    def getField(self, row, col):
        field = row[col].text
        if self.isEmptyField(field):
                return ''
            
        return field.strip()
 
    
    #   Extract the player data for a row.
    def getPlayerData(self, row):
            field_list = []
            
            player_name = self.getField(row,PLAYER_NAME_FIELD)
            total_points = self.getField(row,TOTAL_POINTS_FIELD)
            time = self.getField(row, TIME_FIELD)
            shot_1 = self.getField(row, SHOT1_FIELD)
            shot_1_tot = self.getField(row, SHOT1_MAKE_FIELD)
            shot_2 = self.getField(row, SHOT2_FIELD)
            shot_2_tot = self.getField(row, SHOT2_MAKE_FIELD)
            shot_3 = self.getField(row, SHOT3_FIELD)
            shot_3_tot = self.getField(row, SHOT3_MAKE_FIELD)
            rebouts = self.getField(row, REBOUTS_FIELD)
            assists = self.getField(row, ASSISTS_FIELD)
            faults = self.getField(row, FOULS_FIELD)
            faults_receibed = self.getField(row, FOULS_RECEIVED_FIELD)
            
            field_list.append(player_name)
            field_list.append(time)
            field_list.append(total_points)
            
            field_list.append(shot_1)
            field_list.append(shot_1_tot)
            
            field_list.append(shot_2)
            field_list.append(shot_2_tot)
    
            field_list.append(shot_3)
            field_list.append(shot_3_tot)
            
            field_list.append(rebouts)
            field_list.append(assists)
            field_list.append(faults)
            field_list.append(faults_receibed)
            
            return field_list
   
        
    #   Return the players data for a team in a game       
    def getTeamPlayer(self, game_data, team):
        players_list= []

        players = team.find('tbody').find_all('tr')
        for player in players:
            fields = player.findAll('td')
            if self.isPlayer(fields):
                player_data = self.getPlayerData(fields)
                players_list.append(game_data + player_data)
        
        return players_list   


    #   Return the players data in a game.  
    def getGamePlayers(self, game_id):
        game_data = []
        local_players = []
        visit_players = []
        
        url = GAME_STATISTICS_URL.format(game_id)
        response= utils.getRequest( url, self.logger )
        soup = BeautifulSoup(response.text,"html.parser")
      
        date = soup.find('div', {'class','page-title'}).text[0:11].strip()
        
        teams = soup.findAll('div', {'class','rd-statistic-table'})
        if teams:
            local_team = teams[0].table.tr.th.text    
            visit_team = teams[1].table.tr.th.text       
            game_result = soup.find('div', {'class', 'game-total-result'}).text.split('-')
            local_team_points = game_result[0].strip()
            visit_team_points = game_result[1].strip()
             
            game_data.append(LEGA_NAME)
            game_data.append(date)
            game_data.append(local_team)
            game_data.append(local_team_points)
            game_data.append(visit_team)
            game_data.append(visit_team_points)
            
            game_data.append('local')
            local_players = self.getTeamPlayer(game_data, teams[0])
            
            game_data[6] ='visit'
            visit_players = self.getTeamPlayer(game_data, teams[1])
        
        return local_players + visit_players    

    
    #   Return the games played for a team in a season
    def getTeamGames(self, team_id, season):
        
        url = GAMES_URL.format(team_id, season)
        response= utils.getRequest(url, self.logger)
        soup = BeautifulSoup(response.text,"html.parser")
        
        games_ids=[]
        
        if soup.find('div',{'class':'orange-background'}):
            return games_ids
        
        games = soup.find('div',{'class':'rd-statistic-table'}).table
        games = games.findAll('tr')
        
        for game in games:
            if game.td and game.td.a:
                games_ids.append(game.td.a.get('href').split('/')[4])
                  
        return games_ids

    #   Return the games play for a team in a season
    def getSeasonTeams(self, season):
        teams_ids = []
        
        url = SEASON_TEAMS_URL.format(season)
        response = utils.getRequest(url, self.logger)
        soup = BeautifulSoup(response.text,"html.parser")
        
        teams = soup.find('select', {'name':'club'}).findAll('option')
        
        for team in teams:
            team_id = team.get('value')
            if team_id and team_id!='':
                teams_ids.append(team.get('value'))
            
        return teams_ids

    #   Return the teams for a season
    def getSeasonPlayers(self, season):
        
        player_list = []
        teams_ids = self.getSeasonTeams(season)
        for team_id in teams_ids:
            #print(team_id)
            self.logger.info('Get team games from {0} team'.format(team_id))
            season_games = self.getTeamGames(team_id, season)
        
            for game_id in season_games:
                self.logger.info('Get players from {0} game'.format(game_id))
                #print(game_id)
                players = self.getGamePlayers(game_id)
                player_list = player_list + players
            
        return player_list   