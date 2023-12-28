import pandas as pd
import numpy as np
import enum

# Here you can add any global configuations

color_list1 = ["green", "blue"]
color_list2 = ["red", "purple"]

df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
df_player_combined_keepers = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')


country_list = df_player_combined['team'].unique()
country_list.sort()


# TODO: create enum converting bad names to good names 
attributes_players = list(df_player_combined.select_dtypes(include=[np.number]).columns.values)
attributes_keepers = list(df_player_combined_keepers.select_dtypes(include=[np.number]).columns.values)
attributes_players.sort()
attributes_keepers.sort()