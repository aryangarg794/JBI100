from plotly_football_pitch import make_pitch_figure, PitchDimensions, VerticalStripesBackground
from ..config import COUNTRY_LIST, ATTRIBUTES_PLAYERS, ATTRIBUTES_KEEPERS

from dash import dcc, html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


import copy


class BestPlayersPitch(html.Div):

    def __init__(self):
        self.name = "pitch"
        self.name_player_graph = "pitch-player-graph"
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
                make_filter_boxes(),
                dcc.Graph(
                    id=self.name
                ),
                html.Div(
                    id="player-card",
                    children=[
                        html.Div(
                            id="left-column-player",
                            style={"background" : "#111111", "color" : "white", "display" : "flex", 
                                   "justify-content" : "center", "align-items" : "center",}
                        ),
                        dcc.Graph(
                            id=self.name_player_graph, 
                            figure=self.blank_fig(),
                        )
                    ],
                    style={"display" : "flex", "flex-direction" : "row"}
                )
            ]
        )

    #############################################################################################################################
    # blank_fig refactored from https://stackoverflow.com/questions/66637861/how-to-not-show-default-dcc-graph-template-in-dash #
    #############################################################################################################################
        
    def blank_fig(self):

        self.fig = go.Figure(go.Scatter(x=[], y = []))
        self.fig.update_layout(template = None)
        self.fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
        self.fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

        return self.fig

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

        self.fig = make_pitch_figure(self.dimensions, pitch_background=self.background, marking_colour="white", marking_width=4)

        # add attackers

        text_attacker = best_forwards['player'].values.tolist()
        self.fig.add_trace(go.Scatter(
            x=[80, 90, 80],
            y=[10, 35, 63],
            mode="markers+text",
            name="Lines, Markers and Text",
            showlegend=False,
            customdata=best_forwards,
            hovertemplate="<b>%{customdata[0]} (%{customdata[1]}) </b> <br>" +
            "<b>Age:</b> %{customdata[3]} <br>" +
            "<b>Country:</b> %{customdata[2]} <br>" + 
            "<b>Goals:</b> %{customdata[122]} <br>" +
            "<b>xG:</b> %{customdata[134]} <br>" +
            "<b>Shots on Target:</b> %{customdata[124]} <br>" +
            "<extra></extra>",
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
            customdata=best_midfielders,
            hovertemplate="<b>%{customdata[0]} (%{customdata[1]}) </b> <br>" +
            "<b>Age:</b> %{customdata[3]} <br>" +
            "<b>Country:</b> %{customdata[2]} <br>" + 
            "<b>Assists:</b> %{customdata[66]} <br>" +
            "<b>Passes:</b> %{customdata[53]} <br>" +
            "<b>Through Balls:</b> %{customdata[78]} <br>" +
            "<extra></extra>",
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
            customdata=best_defenders,
            hovertemplate="<b>%{customdata[0]} (%{customdata[1]}) </b> <br>" +
            "<b>Age:</b> %{customdata[3]} <br>" +
            "<b>Country:</b> %{customdata[2]} <br>" + 
            "<b>Interceptions:</b> %{customdata[18]} <br>" +
            "<b>Tackles:</b> %{customdata[6]} <br>" +
            "<b>Bookings:</b> %{customdata[40]} <br>" +
            "<extra></extra>",
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
            customdata=best_keeper,
            hovertemplate="<b>%{customdata[0]} (%{customdata[1]}) </b> <br>" +
            "<b>Age:</b> %{customdata[3]} <br>" +
            "<b>Country:</b> %{customdata[2]} <br>" + 
            "<b>Clean Sheets:</b> %{customdata[18]} <br>" +
            "<b>Saves:</b> %{customdata[13]} <br>" +
            "<b>Crosses Stopped:</b> %{customdata[44]} <br>" +
            "<extra></extra>",
            text=text_goalkeeper,
            textposition="top center"
        ))

        self.fig.update_layout(
            title_text="Best players in each position",
            title_font_size=35,
            template="plotly_dark"
        )
        return self.fig
    
    def normalize(self, attr_max, attr_min, value):
        return (value - attr_min)/(attr_max-attr_min)
    
    def update_player(self, player, position, selected_attributes):

        if position == 'GK':
            df_player = self.df_keepers_combined.loc[self.df_keepers_combined['player']==player]
        else:
            df_player = self.df_player_combined.loc[self.df_player_combined['player']==player]


        display_attributes = df_player[selected_attributes].T.values.tolist()

        colors = []
        for attribute in selected_attributes:
            value = df_player[attribute].values[0]
            if position == "GK":
                attr_max = self.df_keepers_combined[attribute].max()
                attr_min = self.df_keepers_combined[attribute].min()
            else:
                attr_max = self.df_player_combined[attribute].max()
                attr_min = self.df_player_combined[attribute].min()

            norm_value = self.normalize(attr_max, attr_min, value)
            colors.append(f'rgba(124,252,0,{norm_value})')

        self.fig = go.Figure()
        self.fig.add_trace(
            go.Table(
                cells=dict(values=[df_player[selected_attributes].columns, display_attributes],
                            fill_color=['black', np.array(colors)],
                            align='left')
            )
        )
        self.fig.for_each_trace(lambda t: t.update(header_fill_color = 'rgba(0,0,0,0)'))
        self.fig.update_layout(template="plotly_dark")

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
                    options=[{"label": i, "value": i} for i in COUNTRY_LIST],
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
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
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
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
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
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
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
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
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





        

