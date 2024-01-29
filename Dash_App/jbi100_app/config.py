import pandas as pd
import numpy as np
import enum

# Here you can add any global configuations

df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
df_player_combined_keepers = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')

PLAYER_LIST_OUTFIELD = df_player_combined['player']
PLAYER_LIST2_KEEPERS = df_player_combined_keepers['player']
PLAYER_LIST = pd.concat([PLAYER_LIST_OUTFIELD, PLAYER_LIST2_KEEPERS])

COUNTRY_LIST = df_player_combined['team'].unique()
COUNTRY_LIST.sort()

ATTRIBUTES_PLAYERS = list(df_player_combined.select_dtypes(include=[np.number]).columns.values)
ATTRIBUTES_KEEPERS = list(df_player_combined_keepers.select_dtypes(include=[np.number]).columns.values)
ATTRIBUTES_PLAYERS.sort()
ATTRIBUTES_KEEPERS.sort()


