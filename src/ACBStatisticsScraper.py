#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 18:09:00 2020

@author: Juan Penalta Rodríguez y Michaelle Valenzuela Sangoquiza
"""
from bs4 import BeautifulSoup
import Utils as utils

PLAYER_NAME_FIELD = 1
TOTAL_POINTS_FIELD = 2
TIME_FIELD = 3
SHOT1_FIELD = 4
SHOT2_FIELD = 6
SHOT3_FIELD = 8
REBOUTS_FIELD = 10
ASSISTS_FIELD = 12
FOULS_FIELD = 19
FOULS_RECEIVED_FIELD = 20
ACB_NAME='ACB'

STATISTICS_URL = 'http://acb.com/partido/estadisticas/id/{0}' 
GAMES_URL = 'http://acb.com/club/partidos/id/{0}/temporada_id/{1}/filtro_id/4'
SEASON_TEAMS_URL = 'http://acb.com/club/index/temporada_id/{0}'

class ACBScraper:
    
    def __init__(self):
        self.logger = utils.getLogger('ACBScrapper')

    #   Check if it is a row that contains player data.
    def isPlayer(self, fields):
        return len(fields)>5 and fields[1].text!='Total'  and fields[1].text!='Equipo' and fields[1].text!='Equipo'
 
    #   Check if the value is a not valid data.    
    def isEmptyField(self, value):
        return value == None or value =='\xa0'

    #   Return the value of the column if it is a valid value or a empty string
    #   in other case.
    def getField(self, fields, col):
        field = fields[col].text
        if self.isEmptyField(field):
                return ''
            
        return field

    #   Split in get and make fields the field of shots values get/make 
    def splitPlayerShots(self, shots):
        shots_split = ['0','0']
        if shots !='':
            shots_split = shots.split('/')
    
        return shots_split

    #   Extract the player data of a row.        
    def getPlayerData(self, fields):
            field_list = []
            
            player_name = self.getField(fields,PLAYER_NAME_FIELD)
            total_points = self.getField(fields,TOTAL_POINTS_FIELD)
            time = self.getField(fields, TIME_FIELD)
            shot_1 = self.getField(fields, SHOT1_FIELD)
            shot_2 = self.getField(fields, SHOT2_FIELD)
            shot_3 = self.getField(fields, SHOT3_FIELD)
            rebouts = self.getField(fields, REBOUTS_FIELD)
            assists = self.getField(fields, ASSISTS_FIELD)
            faults = self.getField(fields, FOULS_FIELD)
            faults_receibed = self.getField(fields, FOULS_RECEIVED_FIELD)
            
            field_list.append(player_name)
            field_list.append(time)
            field_list.append(total_points)
            
            shot_split = self.splitPlayerShots(shot_1)
            field_list.append(shot_split[0])
            field_list.append(shot_split[1])
            
            shot_split = self.splitPlayerShots(shot_2)
            field_list.append(shot_split[0])
            field_list.append(shot_split[1])
    
            shot_split = self.splitPlayerShots(shot_3)
            field_list.append(shot_split[0])
            field_list.append(shot_split[1])
            
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
        
        url =STATISTICS_URL.format(game_id)
        response= utils.getRequest(url, self.logger)  
        soup = BeautifulSoup(response.text,"html.parser")
      
        date = soup.find('div', {'class':'datos_evento'}).find("span").text
        
        teams = soup.findAll('section', {'class':'partido'})
        if teams:
            local_team = teams[0].find('h6').text.split('\xa0\xa0')
            visit_team = teams[1].find('h6').text.split('\xa0\xa0')
        
            game_data.append(ACB_NAME)
            game_data.append(date)
    
            game_data = game_data + local_team
            game_data = game_data + visit_team
      
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
     
        games = soup.findAll('td',{'class':'partido'})
        if games:
            for game in games:
                my_team = game.findAll('span',{'class':'abreviatura'})[0]
                if my_team.find('a',{'class':'mi_equipo'}):
                    game_link = my_team.a.get('href')
                    if game_link.startswith('/partido/ver/id'):
                        games_ids.append(my_team.a.get('href').split('/')[4])
                  
        return games_ids
 
    #   Return the teams for a season
    def getSeasonTeams(self, season):
        url = SEASON_TEAMS_URL.format(season)
        response = utils.getRequest(url, self.logger)
        soup = BeautifulSoup(response.text,"html.parser")
        
        teams_list = soup.findAll('article',{'class':'club'})
        teams_ids = []
        
        for team in teams_list:
            team_id = team.h4.a.get('href').split('/')[4]
            teams_ids.append(team_id)
            
        return teams_ids
        
    #  Return de players data for a season.    
    def getSeasonPlayers(self, season):
        
        player_list = []
        teams_ids = self.getSeasonTeams(season)
        
        for team_id in teams_ids:
            self.logger.info('Get team games from {0} team'.format(team_id))
            season_games = self.getTeamGames(team_id, season)
        
            for game_id in season_games:
                self.logger.info('Get players from {0} game'.format(game_id))
                players = self.getGamePlayers(game_id)
                player_list = player_list + players
            
        return player_list    
