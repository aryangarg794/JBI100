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


class CompareIdea2(html.Div):
    def __init__(self):
        self.df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')

        super().__init__(
            className="compare-idea-2",
            children=[
                html.H1("Soccer Player Comparison"),
                make_filter_boxes(),
                dcc.Graph(
                    id='compare-bar',
                    style={'clickData' : 'event'},
                ),
            ]
        )

    def update_compare_idea2_chart(self, player1, player2, selected_stat):
        df_compare = copy.deepcopy(self.df_player_combined)

        

        # Select data for the chosen stat
        df1 = df_compare[['player', selected_stat]]

        df_player1 = df1.loc[df1["player"] == player1]
        val_player1 = df_player1.iloc[0][selected_stat]
        val_player1

        df_player2 = df1.loc[df1["player"] == player2]
        val_player2 = df_player2.iloc[0][selected_stat]
        val_player2

        self.fig = go.Figure()
        self.fig.add_trace(go.Bar(x=[player1, player2], y=[val_player1, val_player2], marker_color=['blue', 'orange']))
        self.fig.update_layout(title=f'{selected_stat} Comparison', template="plotly_dark")

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
                            id="player1-dropdown",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value="Harry Kane",
                            searchable=True,
                            placeholder="Select Player", 
                        ),
                ],
                style={"width": "20%", "margin-bottom": "15px"}
            ),

            html.Div(
                id="chose-player2",
                children=[
                    html.Label("Player 2:"),
                        dcc.Dropdown(
                            id="player2-dropdown",
                            options=[{"label": i, "value": i} for i in PLAYER_LIST],
                            value="Jude Bellingham",
                            searchable=True,
                            placeholder="Select Player", 
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
