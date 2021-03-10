#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import json
import ast
import re


# In[2]:


from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.endpoints import BoxScoreDefensive
from nba_api.stats.library import data
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.endpoints import boxscorematchups

pd.set_option('display.max_columns', None)


# In[3]:


player_dict = players.get_players()


# In[5]:


steph = [player for player in player_dict if player['full_name'] == 'Stephen Curry'][0]


# In[6]:


steph


# In[7]:


steph_id = steph['id']


# In[8]:


team_dict = teams.get_teams()


# In[10]:


gsw = [team for team in team_dict if team['abbreviation'] == "GSW"][0]


# In[11]:


gsw_id = gsw['id']


# In[13]:


warriors_gl = teamgamelog.TeamGameLog(gsw_id)


# In[14]:


warriors_20_df = warriors_gl.get_data_frames()[0]


# In[15]:


warriors_20_df[warriors_20_df['MATCHUP'].str.contains('SAS')]


# In[16]:


gamelog_steph = playergamelog.PlayerGameLog(steph_id)


# In[17]:


gamelog_steph_df = gamelog_steph.get_data_frames()[0]


# In[18]:


gamelog_steph_df.head(2)


# In[19]:


gamelog_steph_df['PAR'] = gamelog_steph_df['PTS'] + gamelog_steph_df['AST'] + gamelog_steph_df['REB'] 


# In[20]:


gamelog_steph_df.head(2)


# In[21]:


gamelog_steph_df['PAR'].mean()


# In[22]:


brogdon = [player for player in player_dict if player['full_name'] == 'Malcolm Brogdon'][0]


# In[23]:


brogdon_id = brogdon['id']


# In[24]:


gamelog_brogdon_20 = playergamelog.PlayerGameLog(brogdon_id, '2020')
gamelog_brogdon_19 = playergamelog.PlayerGameLog(brogdon_id, '2019')
gamelog_brogdon_18 = playergamelog.PlayerGameLog(brogdon_id, '2018')
gamelog_brogdon_17 = playergamelog.PlayerGameLog(brogdon_id, '2017')


# In[25]:


gamelog_brogdon_20_df = gamelog_brogdon_20.get_data_frames()[0]
gamelog_brogdon_19_df = gamelog_brogdon_19.get_data_frames()[0]
gamelog_brogdon_18_df = gamelog_brogdon_18.get_data_frames()[0]
gamelog_brogdon_17_df = gamelog_brogdon_17.get_data_frames()[0]


# In[26]:


brog_17to20_df = pd.concat([gamelog_brogdon_17_df, gamelog_brogdon_18_df, gamelog_brogdon_19_df, gamelog_brogdon_20_df])


# In[27]:


brog_17to20_df['GAME_DATE'] = pd.to_datetime(brog_17to20_df['GAME_DATE'])


# In[28]:


brog_17to20_df.sort_values(by='GAME_DATE', ascending=False,inplace=True)


# In[29]:


brog_17to20_df.head(2)


# In[30]:


brog_17to20_df['PAR'] = brog_17to20_df['PTS'] + brog_17to20_df['AST'] + brog_17to20_df['REB'] 


# In[31]:


brog_17to20_df.head(2)


# In[32]:


brog_vs_bkn = brog_17to20_df[brog_17to20_df['MATCHUP'].str.contains('BKN')]


# In[33]:


li_brog_vs_bkn = brog_vs_bkn['Game_ID'].to_list()


# In[36]:


def oppFinder(row):
    return row.split()[-1]


# In[37]:


oppFinder('IND vs. UTA')


# In[38]:


brog_17to20_df['OPPONENT'] = brog_17to20_df['MATCHUP'].apply(oppFinder)


# In[40]:


brog_17to20_df.groupby('OPPONENT').agg(
    AVG_PLUSMINUS = ('PLUS_MINUS', 'mean'),
    AVG_REB = ('REB', 'mean'),
    AVG_STL = ('STL', 'mean'),
    AVG_PTS = ('PTS', 'mean'),
    AVG_AST = ('AST', 'mean'),
    AVG_PAR = ('PAR', 'mean')
 ).round(2)


# ---

# In[43]:


with open('json_nba.json') as f:
    data = json.load(f)


# In[44]:


json_data = ast.literal_eval(data)


# In[45]:


json = json_data[0]


# In[48]:


events = json['events'][0]


# In[50]:


df = pd.json_normalize(events, sep='_')


# In[51]:


df


# In[53]:


competitors = pd.json_normalize(df['competitors'][0])
#competitors of the current game matchup


# In[54]:


competitors


# In[55]:


displayGroups = pd.json_normalize(df['displayGroups'][0])
#types of betting (lines, game&player props, periods)


# In[56]:


displayGroups


# In[58]:


player_props = pd.json_normalize(displayGroups[displayGroups['description'] == 'Player Props']['markets'][3])


# In[60]:


player_props.drop(['status','singleOnly','notes', 'period.abbreviation','period.live'],inplace=True,axis=1)


# In[61]:


player_props.head(2)


# In[64]:


pd.json_normalize(player_props['outcomes'][0])


# In[65]:


player_props.head(1)


# In[67]:


player_props['outcome_ids'] = player_props['outcomes'].apply(lambda x: "|".join(i['id'] for i in x))


# In[68]:


player_props['player_prop_odds'] = player_props['outcomes'].apply(lambda x: "|".join(i['price']['american'] for i in x))


# In[70]:


player_props['yes'] = player_props['player_prop_odds'].apply(lambda x: x.split('|')[0])
player_props['no'] = player_props['player_prop_odds'].apply(lambda x: x.split('|')[1])


# In[72]:


player_props['outcome_yes_id'] = player_props['outcome_ids'].apply(lambda x: x.split('|')[0])
player_props['outcome_no_id'] = player_props['outcome_ids'].apply(lambda x: x.split('|')[1])


# In[74]:


player_props.drop(['outcome_ids', 'player_prop_odds'],axis=1,inplace=True)


# In[77]:


dejounte = [player for player in player_dict if player['full_name'] == 'Dejounte Murray'][0]
demar = [player for player in player_dict if player['full_name'] == 'DeMar DeRozan'][0]


# In[78]:


player_props.iloc[25]['outcomes'][1]


# In[82]:


def isHandicap(row):
    for i in row:
        try:
            return i['price']['handicap']
        except (KeyError):
            return np.nan


# In[83]:


player_props['handicap'] = player_props['outcomes'].apply(isHandicap)


# In[84]:


player_props['player_prop_odds'] = player_props['outcomes'].apply(lambda x: "|".join(i['price']['american'] for i in x))


# In[86]:


player_props.head(1)


# In[87]:


player_props['player_name'] = player_props['descriptionKey'].apply(lambda s: s.split('{',1)[1].split('}')[0]).apply(lambda s: s.split('(')[0])


# In[88]:


player_props['player_team'] = player_props['descriptionKey'].apply(lambda s: s.split('{',1)[1].split('}')[0]).apply(
lambda s: s.split('(',1)[1].split(')')[0])


# In[90]:


unique_team_names = list(player_props['player_team'].unique())


# In[91]:


unique_team_names


# In[92]:


def getOpponent(row):
    for i in unique_team_names:
        if i == row:
            return unique_team_names[-1]
        else:
            return unique_team_names[0]


# In[93]:


player_props['opp_team'] = player_props['player_team'].apply(getOpponent)


# In[94]:


player_props.iloc[0]['descriptionKey']


# In[95]:


player_props.iloc[-7]['descriptionKey'].split(' - {')


# In[96]:


gsw_sas = teamgamelog.TeamGameLog(gsw_id)


# In[97]:


gsw_sas = gsw_sas.get_data_frames()[0]


# In[98]:


gsw_sas.head()


# In[ ]:





# In[101]:


game_datetime = pd.to_datetime(re.findall(r'\d+', df['link'][0])[0][:8])


# In[102]:


game_datetime


# In[103]:


player_props['GAME_DATE'] = game_datetime


# In[104]:


player_props.head(1)


# In[105]:


player_props['MATCHUP'] = player_props['player_team'] + ' @ ' + player_props['opp_team']


# In[107]:


prop_action = ['Double-Double, Total Points', 'Total Rebounds and Assists',
              'Total Points, Rebounds and Assists', 'Total Made 3 Point Shots']


# for i in player_props['descriptionKey']:
#     if i in prop_action:
#         print(prop_action)
#     else:
#         print('not here')

# In[108]:


def getPlayerStats(player_name):
    gets_player_name = [player for player in player_dict if player['full_name'] == player_name][0]
    player_name_id = gets_player_name['id']
    df_player = playergamelog.PlayerGameLog(player_name_id).get_data_frames()[0]
    df_player['PAR'] = df_player['PTS'] + df_player['AST'] + df_player['REB']
    df_player['PA'] = df_player['PTS'] + df_player['AST']
    return df_player


# ---

# In[110]:


players_df = pd.DataFrame(data.players)


# In[111]:


players_df.columns = ['player_id','player_lastname','player_first_name','player_fullname','player_active']


# In[112]:


active_players_df = players_df[players_df['player_active'] == True]


# In[114]:


teams_df = pd.DataFrame(data.teams)


# In[115]:


teams_df.columns = ['team_id','team_abb','team_nickname','team_yr','team_city','team_fullname','team_state']


# In[116]:


teams_df.drop('team_yr',inplace=True,axis=1)


# In[119]:


teams_df[teams_df['team_abb'] == 'DAL']['team_id']


# In[120]:


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


# In[121]:


get_teams_id(['DAL', 'NOP'])


# In[122]:


get_teams_abb([1610612742, 1610612740])


# In[123]:


df1 = teams_df[teams_df['team_abb'] == 'BOS']
df2 = teams_df[teams_df['team_abb'] == 'NOP']


# In[124]:


pd.concat([df1,df2])


# In[125]:


def getTeamRecentGames(team_abb):
    gets_team_name = [team for team in team_dict if team['abbreviation'] == team_abb][0]
    team_name_id = gets_team_name['id']
    df_team = teamgamelog.TeamGameLog(team_name_id).get_data_frames()[0]
    return df_team


# In[126]:


getTeamRecentGames('NOP').head(2)


# In[127]:


getTeamRecentGames('DAL').head(2)


# In[ ]:





# In[ ]:




