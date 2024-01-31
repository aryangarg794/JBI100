from ..config import ATTRIBUTES_PLAYERS, ATTRIBUTES_KEEPERS, PLAYER_LIST, PLAYER_LIST_KEEPERS, PLAYER_LIST_OUTFIELD

from dash import dcc, html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import copy
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update
import copy
import matplotlib
import random


class CompareIdea2(html.Div):
    def __init__(self):
        self.df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.name = "bar-comparison"

        super().__init__(
            className="compare-idea-2",
            id=self.name,
            children=[
                html.H1("Soccer Player Comparison"),
                make_filter_boxes(),
                dcc.Graph(
                    id='compare-bar',
                    style={'clickData' : 'event'},
                ),
            ],
            style={"background" : "#111111", "color" : "white"}
        )

    def normalize(self, max_att, min_att, value):
        return (value-min_att)/(max_att-min_att)

    def update_compare_idea2_chart(self, players, selected_stat):
        df_compare = copy.deepcopy(self.df_player_combined)

        

        # Select data for the chosen stat
        df1 = df_compare[['player', selected_stat]]

        max_att = df_compare[selected_stat].max()
        min_att = df_compare[selected_stat].min()

        values = []
        colors = []

        for player in players:
            df_player = df1.loc[df1["player"] == player]
            val_player = df_player.iloc[0][selected_stat]
            values.append(val_player)
            norm_value = self.normalize(max_att, min_att, val_player)
            colors.append(f'rgba(124,252,0,{norm_value})')

        
        

        self.fig = go.Figure()
        self.fig.add_trace(go.Bar(x=values, y=players, marker_color=colors, hoverinfo='none', orientation='h'))
        self.fig.update_layout(title=f'{selected_stat.replace("_", " ").capitalize()} Comparison for {", ".join(player for player in players)}', 
                               template="plotly_dark")
        
        self.fig.update_xaxes(title_text=selected_stat.replace("_", " ").capitalize())
        self.fig.update_yaxes(title_text='Players')

        return go.FigureWidget(self.fig)



def make_filter_boxes():
    return html.Div(
        id="control-player-comparison",
        children=[
            html.Div(
                id="chose-player",
                children=[
                    html.Label("Player 1:"),
                        dcc.Dropdown(
                            id="player-dropdown",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value=["Harry Kane", "Jude Bellingham", "Lionel Messi"],
                            multi=True,
                            searchable=True,
                            placeholder="Select Players", 
                        ),
                ],
                style={"width": "20%", "margin-bottom": "15px"}
            ),

            html.Div(
                id="stat-dropdown",
                children=[
                html.Label("Size Attribute"),
                dcc.Dropdown(
                    id="pick-attribute",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                    multi=False,
                    value="goals",
                    searchable=True,
                    placeholder="Select Attribute (Keeper Attributes Excluded)", 
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
            ), 
        ],
        style={"display": "flex", "flex-direction": "row", "flex-wrap": "wrap", "width": "100%", "textAlign": "float-left",
            "gap": "35px", "padding": "20px"}
    )
