from dash import dcc, html
from plotly_football_pitch import make_pitch_figure, PitchDimensions, VerticalStripesBackground

import pandas as pd
import plotly.graph_objects as go
import copy


class BestPlayersPitch(html.Div):

    def __init__(self):
        self.name = "pitch"
        self.dimensions = PitchDimensions()
        self.background = VerticalStripesBackground(
            colours=["#81B622", "#72A11E"],
            num_stripes=10,
        )
        self.fig = make_pitch_figure(
            self.dimensions,
            pitch_background=self.background,
        )

        self.df_player_combined       = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.df_keepers_combined      = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')
        self.df_player_valuations     = pd.read_csv('../Data/Player Valuation/simple_valuations.csv', delimiter=',')

        super().__init__(
            className="pitch_players",
            children=[
                dcc.Graph(figure=self.fig)
            ]
        )

    def find_best_players(self, filters={"attack": "goals", "defense":"tackles", "goalkeeper":"gk_clean_sheets", "midfield":"passes"}, 
                         miscellaneous_filters = {"age" : ["higher", 0], "value" : ["higher", 0], "country" : ["France", "argentina", "netherlands"]}):
        
        df_temp_player_combined = copy.deepcopy(self.df_player_combined)
        df_temp_keeper_combined = copy.deepcopy(self.df_keepers_combined)
        df_temp_player_valuations = copy.deepcopy(self.df_player_valuations)

        # sort by age 
        age_filter = miscellaneous_filters["age"]
        if age_filter[0] == "higher":
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['age'] >= age_filter[1]]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['age'] >= age_filter[1]]
        elif age_filter[0] == "lower":
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['age'] <= age_filter[1]]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['age'] <= age_filter[1]]

        # sort by country 
        country_filter = miscellaneous_filters["country"]
        country_filter = [country.capitalize() for country in country_filter]
        if len(country_filter) != 0:
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['team'].isin(country_filter)]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['team'].isin(country_filter)]

        # sort by value
        value_filter = miscellaneous_filters["value"]
        if value_filter[0] == "higher":
            player_list = df_temp_player_valuations.loc[df_temp_player_valuations['market_value_in_eur_y'] >= value_filter[1]]['name'].to_list()
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['player'].isin(player_list)]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['player'].isin(player_list)]
        elif value_filter[0] == "lower":
            player_list = df_temp_player_valuations.loc[df_temp_player_valuations['market_value_in_eur_y'] <= value_filter[1]]['name'].to_list()
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['player'].isin(player_list)]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['player'].isin(player_list)]

        best_forwards = df_temp_player_combined.loc[df_temp_player_combined['position']=='FW'].nlargest(3, filters["attack"])
        best_defenders = df_temp_player_combined.loc[df_temp_player_combined['position']=='DF'].nlargest(4, filters["defense"])
        best_midfielders = df_temp_player_combined.loc[df_temp_player_combined['position']=='MF'].nlargest(3, filters["midfield"])
        best_keeper = df_temp_keeper_combined.loc[df_temp_keeper_combined['position']=='GK'].nlargest(1, filters["goalkeeper"])

        print(best_forwards)
        print(best_defenders)
        print(best_midfielders)
        print(best_keeper)







        

