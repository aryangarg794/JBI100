from dash import dcc, html
from plotly_football_pitch import make_pitch_figure, PitchDimensions, VerticalStripesBackground
from ..config import country_list, attributes_keepers, attributes_players

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
        self.html_id = "pitch-1"

        self.df_player_combined       = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.df_keepers_combined      = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')
        self.df_player_valuations     = pd.read_csv('../Data/Player Valuation/simple_valuations.csv', delimiter=',')

        super().__init__(
            className="pitch_players",
            children=[
                html.Div(id="my-output"),
                make_filter_boxes(),
                dcc.Graph(
                    id=self.name
                )
            ]
        )

    def find_best_players(self, filters={"attack": "goals", "defense":"tackles", "goalkeeper":"gk_clean_sheets", "midfield":"passes"}, age_filter=["higher", 0],
                          value=["higher", 0], countries=[]):
        
        df_temp_player_combined = copy.deepcopy(self.df_player_combined)
        df_temp_keeper_combined = copy.deepcopy(self.df_keepers_combined)
        df_temp_player_valuations = copy.deepcopy(self.df_player_valuations)

    
        if age_filter[0] == "higher":
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['age'] >= age_filter[1]]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['age'] >= age_filter[1]]
        elif age_filter[0] == "lower":
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['age'] <= age_filter[1]]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['age'] <= age_filter[1]]

        # sort by country 
        country_filter = [country.capitalize() for country in countries]
        if len(country_filter) != 0:
            df_temp_player_combined = df_temp_player_combined.loc[df_temp_player_combined['team'].isin(country_filter)]
            df_temp_keeper_combined = df_temp_keeper_combined.loc[df_temp_keeper_combined['team'].isin(country_filter)]

        # sort by value
        value_filter = value
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

        return best_forwards, best_defenders, best_midfielders, best_keeper


    def update(self, best_forwards, best_defenders, best_midfielders, best_keeper):

        self.fig = make_pitch_figure(self.dimensions, pitch_background=self.background, marking_width=2)

        # add attackers

        text_attacker = best_forwards['player'].values.tolist()
        self.fig.add_trace(go.Scatter(
            x=[80, 90, 80],
            y=[10, 35, 63],
            mode="markers+text",
            name="Lines, Markers and Text",
            showlegend=False,
            text=text_attacker,
            textposition="top center"
        ))

        # add midfielders 
        text_midfielder = best_midfielders['player'].values.tolist()
        self.fig.add_trace(go.Scatter(
            x=[55, 65, 55],
            y=[10, 35, 63],
            mode="markers+text",
            name="Lines, Markers and Text",
            showlegend=False,
            text=text_midfielder,
            textposition="top center"
        ))

        # add defenders
        text_defender = best_defenders['player'].values.tolist()
        self.fig.add_trace(go.Scatter(
            x=[30, 25, 25, 30],
            y=[10, 25, 45, 63],
            mode="markers+text",
            name="Lines, Markers and Text",
            showlegend=False,
            text=text_defender,
            textposition="top center"
        ))

        # add goalkeeper 
        text_goalkeeper = best_keeper['player'].values.tolist()
        self.fig.add_trace(go.Scatter(
            x=[10],
            y=[34],
            mode="markers+text",
            name="Lines, Markers and Text",
            showlegend=False,
            text=text_goalkeeper,
            textposition="top center"
        ))
        return self.fig



def make_filter_boxes():
    return html.Div(
        id="control-pitch-card",
        children=[
            html.Div(
                id="country-picker",
                children=[
                html.Label("Country"),
                dcc.Dropdown(
                    id="select-countries-pitch",
                    options=[{"label": i, "value": i} for i in country_list],
                    multi=True,
                    value=None,
                    searchable=True,
                    placeholder="Select countries", 
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ),
            html.Div(
                id="age-picker",
                children=[
                html.Label("Age"),
                dcc.Dropdown(
                    id="select-age-higherlower",
                    options=[{"label": "Higher than", "value": "higher"}, {"label": "Lower than", "value": "lower"}],
                    value="higher", 
                    clearable=False,
                ),
                dcc.Input(
                    id="select-age-input",
                    type="number",
                    value=0
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "gap" : "10px"}
            ),
            html.Div(
                id="value-picker",
                children=[
                html.Label("Value"),
                dcc.Dropdown(
                    id="select-value-higherlower",
                    options=[{"label": "Higher than", "value": "higher"}, {"label": "Lower than", "value": "lower"}],
                    value="higher",
                    clearable=False,
                ),
                dcc.Input(
                    id="select-value-input",
                    type="number",
                    value=0
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "gap" : "10px"}
            ),
            html.Div(
                id="attacker-picker",
                children=[
                html.Label("Attacker Attribute"),
                dcc.Dropdown(
                    id="select-attacker-pitch",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in attributes_players],
                    value="goals",
                    searchable=True,
                    clearable=False,
                    placeholder="Select an attribute for midfielder",
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ),
            html.Div(
                id="midfielder-picker",
                children=[
                html.Label("Midfielder Attribute"),
                dcc.Dropdown(
                    id="select-midfielder-pitch",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in attributes_players],
                    value="passes",
                    searchable=True,
                    clearable=False,
                    placeholder="Select an attribute for midfielder",
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ),
            html.Div(
                id="defender-picker",
                children=[
                html.Label("Defender Attribute"),
                dcc.Dropdown(
                    id="select-defender-pitch",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in attributes_players],
                    value="tackles",
                    searchable=True,
                    clearable=False,
                    placeholder="Select an attribute for defenders",
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ),
            html.Div(
                id="gk-picker",
                children=[
                html.Label("Keeper Attribute"),
                dcc.Dropdown(
                    id="select-keeper-pitch",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in attributes_keepers],
                    value="gk_clean_sheets",
                    searchable=True,
                    clearable=False,
                    placeholder="Select an attribute for keepers",
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ),
        ], style={"display" : "flex", "flex-direction" : "row", "flex-wrap" : "wrap", "width" : "100%", "textAlign": "float-left", "gap" : "35px", 
                  "padding" : "20px"}
    )





        

