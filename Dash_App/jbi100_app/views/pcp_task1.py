from ..config import ATTRIBUTES, ATTRIBUTES_KEEPERS, ATTRIBUTES_PLAYERS


import copy
import pandas as pd

from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px



class PCPTask1(html.Div):

    def __init__(self):
        self.name = "pcp-plot" # name for the intitial pcp plot
        self.name_scatter = "scatter-task1" # name for the auxiliary scatter plot

        self.df_player_combined       = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.df_keepers_combined      = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined_keepers.csv', delimiter=',')
        self.df_player_valuations     = pd.read_csv('../Data/Player Valuation/simple_valuations.csv', delimiter=',')

        super().__init__(
            className="pcp",
            children=[
                self.keepers_or_players(), # query whether we are comparing player attributes or keeper attributes
                html.Div(
                    id="filter-pcp-plot", # div which is used to hold the specific filters for the pcp based on previous filter
                    children=[ 
                    ]
                ),
                html.Div(
                    id="pcp-graphs",
                    children=[
                        dcc.Graph(  # pcp plot
                            id=self.name,
                            style={"width" : "100%"}
                        ),
                        dcc.Graph(  # scatter plot
                            id=self.name_scatter,
                            style={"width" : "100%"}
                        )
                    ],
                    style={"display" : "flex", "flex-direction" : "row", "width" : "100%"}
                )
            ],
        )

    def update_pcp(self, attribute1, attribute2, attribute3, attribute4):

        fig = go.Figure()

        # we choose the relevant df based on which attributes we are looking at
        if attribute1 in ATTRIBUTES_KEEPERS:
            df_copy = copy.deepcopy(self.df_keepers_combined)
        else:
            df_copy = copy.deepcopy(self.df_player_combined)
            # some keepers are included in the player file so we drop those in order to avoid a division by 0 for ols
            df_copy = df_copy.drop(df_copy[df_copy['position'] == 'GK'].index)  


        # renumber positions into categorical numbers such that the graph_object can use it as input
        df_copy['position'].replace(['FW', 'MF', 'DF', 'GK'], [0, 1, 2, 3], inplace=True)
        fig.add_trace(go.Parcoords(
            line=dict(color=df_copy['position']),
            dimensions=list([
                dict(label=attribute1.replace("_", " ").capitalize(), values=df_copy[attribute1]),
                dict(label=attribute2.replace("_", " ").capitalize(), values=df_copy[attribute2]),
                dict(label=attribute3.replace("_", " ").capitalize(), values=df_copy[attribute3]),
                dict(label=attribute4.replace("_", " ").capitalize(), values=df_copy[attribute4]),
            ])
        ))
        
        # change the theme to dark
        fig.update_layout(template="plotly_dark")
        
        return fig
    
    # this function creates the scatter plot 
    def update_scatter(self, attribute1, attribute2):

        # similar to before we select the relevant df based on attribute chosen
        if attribute1 in ATTRIBUTES_KEEPERS:
            df_copy = copy.deepcopy(self.df_keepers_combined)
        else:
            df_copy = copy.deepcopy(self.df_player_combined)
            df_copy = df_copy.drop(df_copy[df_copy['position'] == 'GK'].index)

        # create a express object for a scatter plot with ols trendline and different positions different color
        fig = px.scatter(df_copy, x=attribute1, y=attribute2, trendline='ols', color="position")

        fig.update_layout(template="plotly_dark", 
                          title_text=f"Comparison of {attribute1.replace('_', ' ').capitalize()} and {attribute2.replace('_', ' ').capitalize()}")
        
        fig.update_xaxes(title_text=attribute1.replace("_", " ").capitalize())
        fig.update_yaxes(title_text=attribute2.replace("_", " ").capitalize())

        return fig
    
    # function to create filter boxes if the type of attribute chosen in player type
    def make_attribute_selection_outfield(self):
        return html.Div(
            id="attribute-selection-pcp",
            children=[
                html.Div(
                    id="attr-pcp-1",
                    children=[
                        html.Label("Choose Attribute 1 (x-axis for the scatter on the right)"), 
                        dcc.Dropdown(
                            id="pcp-attribute-1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value='xg',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-2",
                    children=[
                        html.Label("Choose Attribute 2 (y-axis for the scatter on the right)"), 
                        dcc.Dropdown(
                            id="pcp-attribute-2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value='goals',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-3",
                    children=[
                        html.Label("Choose Attribute 3"), 
                        dcc.Dropdown(
                            id="pcp-attribute-3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value='passes',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-4",
                    children=[
                        html.Label("Choose Attribute 4"), 
                        dcc.Dropdown(
                            id="pcp-attribute-4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                            value='assists',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                )
            ],
            style={"display" : "flex", "flex-direction" : "row", "width" : "100%", "padding" : "10px", "gap" : "50px", "background" : "#111111", 
                   "color" : "white"}
        )
    
    # function to create filter boxes if the attribute type chosen is keeper
    def make_attribute_selection_keepers(self):
        return html.Div(
            id="attribute-selection-pcp",
            children=[
                html.Div(
                    id="attr-pcp-1",
                    children=[
                        html.Label("Choose Attribute 1"), 
                        dcc.Dropdown(
                            id="pcp-attribute-1",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
                            value='gk_games',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-2",
                    children=[
                        html.Label("Choose Attribute 2"), 
                        dcc.Dropdown(
                            id="pcp-attribute-2",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
                            value='gk_goals_against',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-3",
                    children=[
                        html.Label("Choose Attribute 3"), 
                        dcc.Dropdown(
                            id="pcp-attribute-3",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
                            value='gk_passes',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                ),
                html.Div(
                    id="attr-pcp-4",
                    children=[
                        html.Label("Choose Attribute 4"), 
                        dcc.Dropdown(
                            id="pcp-attribute-4",
                            options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
                            value='gk_crosses_stopped',
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
                )
            ],
            style={"display" : "flex", "flex-direction" : "row", "width" : "100%", "padding" : "10px", "gap" : "50px", "background" : "#111111", 
                   "color" : "white"}
        )
    
    # function to create initial filter box to choose the type of attribute that is being analysed
    def keepers_or_players(self):
        return html.Div(
            id="choose-version",
            children=[
                html.Label("Choose type of attribute"),
                dcc.Dropdown(
                    id="keepers-or-players",
                    options=["Player Attributes", "Keeper Attributes"],
                    multi=False,
                    value="Player Attributes",
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "background" : "#111111", "color" : "white", "padding" : "10px 10px 10px 10px"}
        )
