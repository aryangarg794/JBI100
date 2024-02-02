import pandas as pd
import numpy as np


df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
df_player_combined_keepers = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')


# list of outfield players
PLAYER_LIST_OUTFIELD = df_player_combined['player']
# list of keepers
PLAYER_LIST_KEEPERS = df_player_combined_keepers['player']
# full list
PLAYER_LIST = pd.concat([PLAYER_LIST_OUTFIELD, PLAYER_LIST_KEEPERS])

# list of countries
COUNTRY_LIST = df_player_combined['team'].unique()
COUNTRY_LIST.sort()

# list of attributes such that they are numerical and not text-based
ATTRIBUTES_PLAYERS = list(df_player_combined.select_dtypes(include=[np.number]).columns.values)
ATTRIBUTES_KEEPERS = list(df_player_combined_keepers.select_dtypes(include=[np.number]).columns.values)
ATTRIBUTES_PLAYERS.sort()
ATTRIBUTES_KEEPERS.sort()

# both attributes combined
ATTRIBUTES = ATTRIBUTES_KEEPERS + ATTRIBUTES_PLAYERS
ATTRIBUTES.sort()

