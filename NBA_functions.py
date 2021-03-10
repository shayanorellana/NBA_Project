#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import json
import ast
import re


# In[ ]:


from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import BoxScoreDefensive
from nba_api.stats.library import data
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.endpoints import boxscorematchups

pd.set_option('display.max_columns', None)


# In[ ]:


player_dict = players.get_players()


# In[ ]:


steph = [player for player in player_dict if player['full_name'] == 'Stephen Curry'][0]


# In[ ]:


steph


# In[ ]:


steph_id = steph['id']


# In[ ]:


team_dict = teams.get_teams()


# In[ ]:


gsw = [team for team in team_dict if team['abbreviation'] == "GSW"][0]


# In[ ]:


gsw_id = gsw['id']


# In[ ]:


warriors_gl = teamgamelog.TeamGameLog(gsw_id)


# In[ ]:


warriors_20_df = warriors_gl.get_data_frames()[0]


# In[ ]:


warriors_20_df[warriors_20_df['MATCHUP'].str.contains('SAS')]


# In[ ]:


gamelog_steph = playergamelog.PlayerGameLog(steph_id)


# In[ ]:


gamelog_steph_df = gamelog_steph.get_data_frames()[0]


# In[ ]:


gamelog_steph_df.head(2)


# In[ ]:


gamelog_steph_df['PAR'] = gamelog_steph_df['PTS'] + gamelog_steph_df['AST'] + gamelog_steph_df['REB'] 


# In[ ]:


gamelog_steph_df.head(2)


# In[ ]:


gamelog_steph_df['PAR'].mean()


# In[ ]:


brogdon = [player for player in player_dict if player['full_name'] == 'Malcolm Brogdon'][0]


# In[ ]:


brogdon_id = brogdon['id']


# In[ ]:


gamelog_brogdon_20 = playergamelog.PlayerGameLog(brogdon_id, '2020')
gamelog_brogdon_19 = playergamelog.PlayerGameLog(brogdon_id, '2019')
gamelog_brogdon_18 = playergamelog.PlayerGameLog(brogdon_id, '2018')
gamelog_brogdon_17 = playergamelog.PlayerGameLog(brogdon_id, '2017')


# In[ ]:


gamelog_brogdon_20_df = gamelog_brogdon_20.get_data_frames()[0]
gamelog_brogdon_19_df = gamelog_brogdon_19.get_data_frames()[0]
gamelog_brogdon_18_df = gamelog_brogdon_18.get_data_frames()[0]
gamelog_brogdon_17_df = gamelog_brogdon_17.get_data_frames()[0]


# In[ ]:


brog_17to20_df = pd.concat([gamelog_brogdon_17_df, gamelog_brogdon_18_df, gamelog_brogdon_19_df, gamelog_brogdon_20_df])


# In[ ]:


brog_17to20_df['GAME_DATE'] = pd.to_datetime(brog_17to20_df['GAME_DATE'])


# In[ ]:


brog_17to20_df.sort_values(by='GAME_DATE', ascending=False,inplace=True)


# In[ ]:


brog_17to20_df.head(2)


# In[ ]:


brog_17to20_df['PAR'] = brog_17to20_df['PTS'] + brog_17to20_df['AST'] + brog_17to20_df['REB'] 


# In[ ]:


brog_17to20_df.head(2)


# In[ ]:


brog_vs_bkn = brog_17to20_df[brog_17to20_df['MATCHUP'].str.contains('BKN')]


# In[ ]:


li_brog_vs_bkn = brog_vs_bkn['Game_ID'].to_list()


# In[ ]:


def oppFinder(row):
    return row.split()[-1]


# In[ ]:


oppFinder('IND vs. UTA')


# In[ ]:


brog_17to20_df['OPPONENT'] = brog_17to20_df['MATCHUP'].apply(oppFinder)


# In[ ]:


brog_17to20_df.groupby('OPPONENT').agg(
    AVG_PLUSMINUS = ('PLUS_MINUS', 'mean'),
    AVG_REB = ('REB', 'mean'),
    AVG_STL = ('STL', 'mean'),
    AVG_PTS = ('PTS', 'mean'),
    AVG_AST = ('AST', 'mean'),
    AVG_PAR = ('PAR', 'mean')
 ).round(2)


# ---

# In[ ]:


with open('json_nba.json') as f:
    data = json.load(f)


# In[ ]:


json_data = ast.literal_eval(data)


# In[ ]:


json = json_data[0]


# In[ ]:


events = json['events'][0]


# In[ ]:


df = pd.json_normalize(events, sep='_')


# In[ ]:


df


# In[ ]:


competitors = pd.json_normalize(df['competitors'][0])
#competitors of the current game matchup


# In[ ]:


competitors


# In[ ]:


displayGroups = pd.json_normalize(df['displayGroups'][0])
#types of betting (lines, game&player props, periods)


# In[ ]:


displayGroups


# In[ ]:


player_props = pd.json_normalize(displayGroups[displayGroups['description'] == 'Player Props']['markets'][3])


# In[ ]:


player_props.drop(['status','singleOnly','notes', 'period.abbreviation','period.live'],inplace=True,axis=1)


# In[ ]:


player_props.head(2)


# In[ ]:


pd.json_normalize(player_props['outcomes'][0])


# In[ ]:


player_props.head(1)


# In[ ]:


player_props['outcome_ids'] = player_props['outcomes'].apply(lambda x: "|".join(i['id'] for i in x))


# In[ ]:


player_props['player_prop_odds'] = player_props['outcomes'].apply(lambda x: "|".join(i['price']['american'] for i in x))


# In[ ]:


player_props['yes'] = player_props['player_prop_odds'].apply(lambda x: x.split('|')[0])
player_props['no'] = player_props['player_prop_odds'].apply(lambda x: x.split('|')[1])


# In[ ]:


player_props['outcome_yes_id'] = player_props['outcome_ids'].apply(lambda x: x.split('|')[0])
player_props['outcome_no_id'] = player_props['outcome_ids'].apply(lambda x: x.split('|')[1])


# In[ ]:


player_props.drop(['outcome_ids', 'player_prop_odds'],axis=1,inplace=True)


# In[ ]:


dejounte = [player for player in player_dict if player['full_name'] == 'Dejounte Murray'][0]
demar = [player for player in player_dict if player['full_name'] == 'DeMar DeRozan'][0]


# In[ ]:


player_props.iloc[25]['outcomes'][1]


# In[ ]:


def isHandicap(row):
    for i in row:
        try:
            return i['price']['handicap']
        except (KeyError):
            return np.nan


# In[ ]:


player_props['handicap'] = player_props['outcomes'].apply(isHandicap)


# In[ ]:


player_props['player_prop_odds'] = player_props['outcomes'].apply(lambda x: "|".join(i['price']['american'] for i in x))


# In[ ]:


player_props.head(1)


# In[ ]:


player_props['player_name'] = player_props['descriptionKey'].apply(lambda s: s.split('{',1)[1].split('}')[0]).apply(lambda s: s.split('(')[0])


# In[ ]:


player_props['player_team'] = player_props['descriptionKey'].apply(lambda s: s.split('{',1)[1].split('}')[0]).apply(
lambda s: s.split('(',1)[1].split(')')[0])


# In[ ]:


unique_team_names = list(player_props['player_team'].unique())


# In[ ]:


unique_team_names


# In[ ]:


def getOpponent(row):
    for i in unique_team_names:
        if i == row:
            return unique_team_names[-1]
        else:
            return unique_team_names[0]


# In[ ]:


player_props['opp_team'] = player_props['player_team'].apply(getOpponent)


# In[ ]:


player_props.iloc[0]['descriptionKey']


# In[ ]:


player_props.iloc[-7]['descriptionKey'].split(' - {')


# In[ ]:


gsw_sas = teamgamelog.TeamGameLog(gsw_id)


# In[ ]:


gsw_sas = gsw_sas.get_data_frames()[0]


# In[ ]:


gsw_sas.head()


# In[ ]:





# In[ ]:


game_datetime = pd.to_datetime(re.findall(r'\d+', df['link'][0])[0][:8])


# In[ ]:


game_datetime


# In[ ]:


player_props['GAME_DATE'] = game_datetime


# In[ ]:


player_props.head(1)


# In[ ]:


player_props['MATCHUP'] = player_props['player_team'] + ' @ ' + player_props['opp_team']


# In[ ]:


prop_action = ['Double-Double, Total Points', 'Total Rebounds and Assists',
              'Total Points, Rebounds and Assists', 'Total Made 3 Point Shots']


# for i in player_props['descriptionKey']:
#     if i in prop_action:
#         print(prop_action)
#     else:
#         print('not here')

# In[ ]:


def getPlayerStats(player_name):
    gets_player_name = [player for player in player_dict if player['full_name'] == player_name][0]
    player_name_id = gets_player_name['id']
    df_player = playergamelog.PlayerGameLog(player_name_id).get_data_frames()[0]
    df_player['PAR'] = df_player['PTS'] + df_player['AST'] + df_player['REB']
    df_player['PA'] = df_player['PTS'] + df_player['AST']
    return df_player


# ---

# In[ ]:


players_df = pd.DataFrame(data.players)


# In[ ]:


players_df.columns = ['player_id','player_lastname','player_first_name','player_fullname','player_active']


# In[ ]:


active_players_df = players_df[players_df['player_active'] == True]


# In[ ]:


teams_df = pd.DataFrame(data.teams)


# In[ ]:


teams_df.columns = ['team_id','team_abb','team_nickname','team_yr','team_city','team_fullname','team_state']


# In[ ]:


teams_df.drop('team_yr',inplace=True,axis=1)


# In[ ]:


teams_df[teams_df['team_abb'] == 'DAL']['team_id']


# In[ ]:


def get_teams_id(teams_abb):
    teams_list = []
    for team in teams_abb:
        teams_list.append(teams_df[teams_df['team_abb'] == team]['team_id'].item())
    return teams_list

def get_teams_abb(teams_id):
    teams_list = []
    for team in teams_id:
        teams_list.append(teams_df[teams_df['team_id'] == team]['team_abb'].item())
    return teams_list


# In[ ]:


get_teams_id(['DAL', 'NOP'])


# In[ ]:


get_teams_abb([1610612742, 1610612740])


# In[ ]:


df1 = teams_df[teams_df['team_abb'] == 'BOS']
df2 = teams_df[teams_df['team_abb'] == 'NOP']


# In[ ]:


pd.concat([df1,df2])


# In[ ]:


def getTeamRecentGames(team_abb):
    gets_team_name = [team for team in team_dict if team['abbreviation'] == team_abb][0]
    team_name_id = gets_team_name['id']
    df_team = teamgamelog.TeamGameLog(team_name_id).get_data_frames()[0]
    return df_team


# In[ ]:


getTeamRecentGames('NOP').head(2)


# In[ ]:


getTeamRecentGames('DAL').head(2)


# In[ ]:





# In[ ]:




