from ..config import ATTRIBUTES_PLAYERS, ATTRIBUTES_KEEPERS, PLAYER_LIST, PLAYER_LIST_KEEPERS, PLAYER_LIST_OUTFIELD

from dash import dcc, html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import copy


class PlayerComparison(html.Div):
    
    def __init__(self):
        self.name = "player-comparison"
        self.df_player_combined       = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.df_keepers_combined      = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')
        self.df_player_valuations     = pd.read_csv('../Data/Player Valuation/simple_valuations.csv', delimiter=',')

        super().__init__(
            id="player-comparison",
            children=[
                self.make_choice_box(),
                html.Div(
                    id="graph-area",
                    children=[]
                )
            ],

        )

    def get_normalized_value(self, df, attribute, player):
        attribute_max = df[attribute].max()
        attribute_min = df[attribute].min()

        value = df[attribute].loc[df['player'] == player].values[0]
        
        return ((value - attribute_min)/(attribute_max-attribute_min))*5

    def update_side_by_side_view(self, player, attribute1, attribute2, attribute3, attribute4):

        
        if player in PLAYER_LIST_OUTFIELD.values:
            df_copy = copy.deepcopy(self.df_player_combined)
        else:
            df_copy = copy.deepcopy(self.df_keepers_combined)


        normalized_attr1 = self.get_normalized_value(df_copy, attribute1, player)
        normalized_attr2 = self.get_normalized_value(df_copy, attribute2, player)
        normalized_attr3 = self.get_normalized_value(df_copy, attribute3, player)
        normalized_attr4 = self.get_normalized_value(df_copy, attribute4, player)      

        attributes = [attribute1.replace("_", " ").capitalize(), attribute2.replace("_", " ").capitalize(), 
                      attribute3.replace("_", " ").capitalize(), attribute4.replace("_", " ").capitalize()]
        radial = [normalized_attr1, normalized_attr2, normalized_attr3, normalized_attr4]

        fig = px.line_polar(r=radial, theta=attributes, line_close=True, range_r=[0, 5], line_shape='spline')
        fig.update_traces(fill='toself')

        fig.update_layout(template="plotly_dark")

        
        return fig
    
    def update_single_graph_view(self, players, attribute1, attribute2, attribute3, attribute4):

        fig = go.Figure()

        df_copy = copy.deepcopy(self.df_player_combined)

        attributes = [attribute1.replace("_", " ").capitalize(), attribute2.replace("_", " ").capitalize(), 
                      attribute3.replace("_", " ").capitalize(), attribute4.replace("_", " ").capitalize()]
        
        attributes_raw = [attribute1, attribute2, attribute3, attribute4] 

        for player in players:
            normalized_attr1 = self.get_normalized_value(df_copy, attribute1, player)
            normalized_attr2 = self.get_normalized_value(df_copy, attribute2, player)
            normalized_attr3 = self.get_normalized_value(df_copy, attribute3, player)
            normalized_attr4 = self.get_normalized_value(df_copy, attribute4, player)

            radial = [normalized_attr1, normalized_attr2, normalized_attr3, normalized_attr4]

            hover_text = []
            for attribute in attributes_raw:
                hover_text.append(("<b>{play}</b><br><b>{attr}</b>: {value} <br>").format(play=player, attr=attribute.replace("_", " ").capitalize(), 
                                                                  value=df_copy[attribute].loc[df_copy['player']==player].values[0]))

            fig.add_trace(go.Scatterpolar(
                name=player,
                r = radial,
                theta=attributes,
                fill='toself',
                line=dict(shape='spline'),
                hovertext=hover_text,
                hoverinfo="text"
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=False
                ),
            ),
            showlegend=True,
            template="plotly_dark"
        )

        fig.for_each_trace(lambda t: t.update(hoveron='points+fills'))

        return fig
    

    def side_by_side(self):
        return html.Div(
            id="side-by-side",
            children=[
                html.Div(
                    id="explain-players",
                    children=[
                        html.Label("Shown are radar graphs which show the relative normalized statistic of an attribute e.g the goals attribute being at 5 does not indicate 5 goals but instead the player had the highest goal tally of the tournament",
                                   style={"margin-bottom" : "35px"}),
                        html.Label("Choose Player 1"),
                        dcc.Dropdown(
                            id="select-player1",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value="Harry Kane",
                            searchable=True,
                            placeholder="Select Player", 
                        ),
                        html.Label("Choose Player 2"),
                        dcc.Dropdown(
                            id="select-player2",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value="Jude Bellingham",
                            searchable=True,
                            placeholder="Select Player", 
                        ),
                        html.Label("Choose Player 3"),
                        dcc.Dropdown(
                            id="select-player3",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value="Lionel Messi",
                            searchable=True,
                            placeholder="Select Player", 
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "justify-content" : "center", "items-align" : "center", "padding" : "10px"}
                ),
                html.Div(
                    id="section-player1",
                    children=[
                        html.Label("Select Attribute 1"),
                        dcc.Dropdown(
                            id="select-player1-attr1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="goals",
                            searchable=True,
                            placeholder="Select Attribute 1", 
                        ),
                        html.Label("Select Attribute 2"),
                        dcc.Dropdown(
                            id="select-player1-attr2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="assists",
                            searchable=True,
                            placeholder="Select Attribute 2", 
                        ),
                        html.Label("Select Attribute 3"),
                        dcc.Dropdown(
                            id="select-player1-attr3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="xg",
                            searchable=True,
                            placeholder="Select Attribute 3", 
                        ),
                        html.Label("Select Attribute 4"),
                        dcc.Dropdown(
                            id="select-player1-attr4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="tackles",
                            searchable=True,
                            placeholder="Select Attribute 4", 
                            style={"margin-bottom" : "25px"}
                        ),
                        dcc.Graph(
                            id="sbs-player1"
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "color" : "white", "justify-content" : "center", 
                           "padding-right" : "10px", "padding-left" : "10px"}
                ), 
                html.Div(
                    id="section-player2",
                    children=[
                        html.Label("Select Attribute 1"),
                        dcc.Dropdown(
                            id="select-player2-attr1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="goals",
                            searchable=True,
                            placeholder="Select Attribute 1", 
                        ),
                        html.Label("Select Attribute 2"),
                        dcc.Dropdown(
                            id="select-player2-attr2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="assists",
                            searchable=True,
                            placeholder="Select Attribute 2", 
                        ),
                        html.Label("Select Attribute 3"),
                        dcc.Dropdown(
                            id="select-player2-attr3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="xg",
                            searchable=True,
                            placeholder="Select Attribute 3", 
                        ),
                        html.Label("Select Attribute 4"),
                        dcc.Dropdown(
                            id="select-player2-attr4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="tackles",
                            searchable=True,
                            placeholder="Select Attribute 4", 
                            style={"margin-bottom" : "25px"}
                        ),
                        dcc.Graph(
                            id="sbs-player2"
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "color" : "white", "justify-content" : "center", 
                           "padding-right" : "10px", "padding-left" : "10px"}
                ),
                html.Div(
                    id="section-player3",
                    children=[
                        html.Label("Select Attribute 1"),
                        dcc.Dropdown(
                            id="select-player3-attr1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="goals",
                            searchable=True,
                            placeholder="Select Attribute 1", 
                        ),
                        html.Label("Select Attribute 2"),
                        dcc.Dropdown(
                            id="select-player3-attr2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="assists",
                            searchable=True,
                            placeholder="Select Attribute 2", 
                        ),
                        html.Label("Select Attribute 3"),
                        dcc.Dropdown(
                            id="select-player3-attr3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="xg",
                            searchable=True,
                            placeholder="Select Attribute 3", 
                        ),
                        html.Label("Select Attribute 4"),
                        dcc.Dropdown(
                            id="select-player3-attr4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="tackles",
                            searchable=True,
                            placeholder="Select Attribute 4", 
                            style={"margin-bottom" : "25px"}
                        ),
                        dcc.Graph(
                            id="sbs-player3"
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "color" : "white", "justify-content" : "center", 
                           "padding-right" : "10px", "padding-left" : "10px"}
                ),
            ],
            style={"background" : "#111111", "display" : "flex", "flex-direction" : "row", "width" : "100%", "padding-top" : "25px", "padding-bottom" : "25px", 
                   "color" : "white"}
        )
    
    def single_view(self):
        return html.Div(
            id="single-view",
            children=[
                html.Div(
                    id="section-players-single",
                    children=[
                        html.Label("Does not work with keepers yet"),
                        html.Label("Choose Players"),
                        dcc.Dropdown(
                            id="select-players-single",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            multi=True,
                            value=["Lionel Messi", "Harry Kane", "Jude Bellingham"],
                            searchable=True,
                            placeholder="Select Players", 
                        ),
                        html.Label("Select Attribute 1"),
                        dcc.Dropdown(
                            id="select-single-attr1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="goals",
                            searchable=True,
                            placeholder="Select Attribute 1", 
                            
                        ),
                        html.Label("Select Attribute 2"),
                        dcc.Dropdown(
                            id="select-single-attr2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="xg",
                            searchable=True,
                            placeholder="Select Attribute 2", 
                            
                        ),
                        html.Label("Select Attribute 3"),
                        dcc.Dropdown(
                            id="select-single-attr3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="assists",
                            searchable=True,
                            placeholder="Select Attribute 3", 
                            
                        ),
                        html.Label("Select Attribute 4"),
                        dcc.Dropdown(
                            id="select-single-attr4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value="dribbles",
                            searchable=True,
                            placeholder="Select Attribute 4", 
                            style={"margin-bottom" : "25px"}
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "background" : "#111111", "color" : "white", "padding" : "10px"}
                ),
                dcc.Graph(
                    id="single-view-graph"
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "justify-content" : "center", "items-align" : "center"}
        )

    def make_choice_box(self):
        return html.Div(
            id="choose-version",
            children=[
                html.Label("Choose type of player comparison"),
                dcc.Dropdown(
                    id="type-of-comparison",
                    options=["Side-by-Side", "Single-Graph"],
                    multi=False,
                    value="Side-by-Side",
                    style={"margin-top" : "5px"}
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "background" : "#111111", "color" : "white", "padding" : "10px 10px 10px 10px"}
        )