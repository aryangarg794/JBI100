from jbi100_app.main import app
from jbi100_app.views.pitch_and_stats import BestPlayersPitch
from jbi100_app.views.twitter_sentiment import TwitterSentiment
from jbi100_app.views.player_comparison import PlayerComparison
from jbi100_app.views.pcp_task1 import PCPTask1
from jbi100_app.views.compare_idea2 import CompareIdea2, make_filter_boxes 
from jbi100_app.config import ATTRIBUTES_KEEPERS, ATTRIBUTES_PLAYERS


from dash import dcc, html, Input, Output
from dash.dependencies import ALL
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class Task2Data():
    
    def __init__(self):
        self.player1 = "Harry Kane"
        self.player2 = "Lionel Messi"
        self.player3 = "Jude Bellingham"

        self.single_view_players = []
        self.bar_view_players = []

    def combine1(self):
        self.single_view_players.append(self.player1)
        self.single_view_players.append(self.player2)
        self.single_view_players.append(self.player3)

        return list(set(self.single_view_players))
    
    def combine2(self):
        self.bar_view_players.append(self.player1)
        self.bar_view_players.append(self.player2)
        self.bar_view_players.append(self.player3)

        return list(set(self.bar_view_players))
    
    def add_players_single_view(self, players):
        for player in players:
            self.single_view_players.append(player)

        return list(set(self.single_view_players))
    
    def add_players_bar(self, players):
        for player in players:
            self.bar_view_players.append(player)

        return list(set(self.bar_view_players))

import re

if __name__ == '__main__':

    # Instantiate custom views
    pitch = BestPlayersPitch()
    sentiment = TwitterSentiment()
    comparison = PlayerComparison()
    compare_idea2 = CompareIdea2()
    pcp = PCPTask1()

    task2data = Task2Data()


    ################################################################
    #                       vis overall code                       #     
    ################################################################

    app.layout = html.Div(
        id="app-container",
        children=[
            html.Div(
                id="navbar",
                children=[
                    html.H1(
                        id="title",
                        className="navbar-title",
                        children=["BeAScout - Visualization tool", 
                                  html.H6(
                                      id="subtitle",
                                      className="navbar-subtitle",
                                      children="Explore the transfermarket"
                                  )],
                        style={"font-weight" : "600"}
                    )
                ], 
                style={"background" : "white", "color" : "black", "padding-top" : "15px", "padding-left" : "50px",
                       "font-family" : "Helvetica", "border-bottom" : "4px solid black"}
            ),

            html.Div(
                id="pcp-div",
                className="pcp-div-1",
                children=[
                    pcp,
                ],
                style={"justify-content" : "center"}
            ),

            html.Div(
                id="pitch-div",
                className="pitch-div-1",
                children=[
                    pitch,
                ],
                style={"justify-content" : "center"}
            ),
            html.Div(
                id="twit-sent",
                className="twit-sent-1",
                children=[
                    sentiment,
                ],
                style={"justify-content" : "center"}
            ),
            html.Div(
                id="player-comp",
                className="comp-1",
                children=[
                    comparison,
                ],
                style={"justify-content" : "center"}
            )
        ],
        style={"display" : "flex", "flex-direction" : "column", "justify-content" : "center", "gap" : "50px", "background" : "white"}
    )

    ################################################################
    #            code for task 1 - relation between factors        #     
    ################################################################

    @app.callback(
        Output("filter-pcp-plot", "children"),
        [Input("keepers-or-players", "value")]
    )
    def update_version(selected_version):
        match selected_version:
            case "Player Attributes":
                return pcp.make_attribute_selection_outfield()
            case "Keeper Attributes":
                return pcp.make_attribute_selection_keepers()
            

    @app.callback(
        Output("pcp-plot", "figure"),
        [Input("pcp-attribute-1", "value"),
         Input("pcp-attribute-2", "value"), 
         Input("pcp-attribute-3", "value"),
         Input("pcp-attribute-4", "value")]
    )
    def update_pcp_plot(selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        return pcp.update_pcp(selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)
    

    @app.callback(
        Output("scatter-task1", "figure"),
        [Input("pcp-attribute-1", "value"),
         Input("pcp-attribute-2", "value")]
    )
    def update_pcp_plot(selected_attribute1, selected_attribute2):
        return pcp.update_scatter(selected_attribute1, selected_attribute2)


    ################################################################
    #                   code for task 2 - pitch plot               #     
    ################################################################

    
    @app.callback(
        Output("pitch", "figure"),
        [Input('select-countries-pitch', 'value'),
         Input('select-age', 'value'),
         Input('select-value', 'value'),
         Input('select-attacker-pitch', 'value'),
         Input('select-midfielder-pitch', 'value'),
         Input('select-defender-pitch', 'value'),
         Input('select-keeper-pitch', 'value'), 
         Input('select-attacker-slider', 'value'),
         Input('select-midfielder-slider', 'value'),
         Input('select-defender-slider', 'value'),
         Input('select-keeper-slider', 'value'),])
    def update_pitch(selected_countries, selected_age, selected_value, selected_attacker_attribute,
                         selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute, selected_attacker_attribute_slider,
                         selected_midfielder_attribute_slider, selected_defender_attribute_slider, selected_keeper_attribute_slider):
        if selected_countries == None:
            input_countries = []
        else:
            input_countries = selected_countries

        best_forwards, best_defenders, best_midfielders, best_keeper = pitch.find_best_players(
            filters={"attack": selected_attacker_attribute, "defense": selected_defender_attribute, "goalkeeper": selected_keeper_attribute, "midfield": selected_midfielder_attribute}, 
            age_filter=selected_age, 
            value_filter=selected_value, 
            countries=input_countries, 
            attribute_keeper_slider=selected_keeper_attribute_slider,
            attribute_defender_slider=selected_defender_attribute_slider,
            attribute_attacker_slider=selected_attacker_attribute_slider,
            attribute_midfielder_slider=selected_midfielder_attribute_slider
        )
        
        return pitch.update(best_forwards, best_defenders, best_midfielders, best_keeper)
    
    @app.callback(
            Output("attributes-and-sliders", "children"), 
            [Input('select-attacker-pitch', 'value'),
            Input('select-midfielder-pitch', 'value'),
            Input('select-defender-pitch', 'value'),
            Input('select-keeper-pitch', 'value'),])
    def on_attribute_change(selected_attacker_attribute, selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute,):
        return pitch.make_filter_boxes_bottom(selected_attacker_attribute, selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute)
    
    @app.callback(
            Output("pitch-player-graph", "figure"), 
            [Input("pitch", 'clickData'),
             Input("select-player-attrs-dropdown", 'value')])
    def on_player_click_graph(click_data, selected_attributes):
        player = click_data['points'][0]['text']
        position = click_data['points'][0]['customdata'][1]
        return pitch.update_player(player, position, selected_attributes)
    
    @app.callback(
            Output("left-column-player", "children"), 
            [Input("pitch", 'clickData')])
    def on_player_click(click_data):
        player = click_data['points'][0]['text']
        position = click_data['points'][0]['customdata'][1]

        df_vals = pd.read_csv("../Data/Player Valuation/simple_valuations.csv")

        value = df_vals["market_value_in_eur_y"].loc[df_vals['name'] == player].values[0]

        if position == "FW":
            BASE_VALUES = ['goals', 'xg', 'pens_made', 'npxg_per_shot', 'minutes', 'dribbles_completed', 'dribbles', 'miscontrols', 'passes_received', 'shots_on_target']
        elif position == "MF":
            BASE_VALUES = ['passes', 'assists', 'aerials_won', 'passes_completed', 'passes_total_distance', 'passes_short', 'passes_medium', 'crosses_into_penalty_area', 'through_balls']
        elif position == "DF":
            BASE_VALUES = ['tackles', 'interceptions', 'tackles_interceptions', 'blocked_shots', 'blocked_passes', 'blocks', 'dribbled_past', 'tackles_won']
        else:
            BASE_VALUES = ['gk_goals_against', 'gk_saves']

        if position == 'GK':
            div = html.Div(
            id="select-player-attrs",
            children=[
                f"{player}, {position}, {value}",
                dcc.Dropdown(
                    id="select-player-attrs-dropdown",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_KEEPERS],
                    multi=True,
                    value=BASE_VALUES,
                    searchable=True,
                    clearable=False,
                    placeholder="Select attributes to display",
                    style={"margin-top" : "5px"}
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "width" : "100%"}
            )
        else:
            div = html.Div(
            id="select-player-attrs",
            children=[
                f"{player}, {position}, {value}",
                dcc.Dropdown(
                    id="select-player-attrs-dropdown",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                    multi=True,
                    value=BASE_VALUES,
                    searchable=True,
                    clearable=False,
                    placeholder="Select attributes to display",
                    style={"margin-top" : "5px"}
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "width" : "100%"}
            )
        return div




    ################################################################
    #           code for task 4 - twitter sentiment analysis       #     
    ################################################################



    @app.callback(
        Output("bar-chart", "figure"),
        [Input("twit-scat", "hoverData")]
    )
    def update_bar_chart(click_data):
        selected_player = click_data['points'][0]['text'].split('<br>')[0]
        player = re.sub(r'\([^)]*\)', '', selected_player).strip()
        positive_tweets = int(click_data['points'][0]['text'].split('<br>')[-3].split(': ')[1])
        neutral_tweets = int(click_data['points'][0]['text'].split('<br>')[-2].split(': ')[1])
        negative_tweets = int(click_data['points'][0]['text'].split('<br>')[-1].split(': ')[1])

        return sentiment.update_fig_bar(player, positive_tweets, neutral_tweets, negative_tweets)
    
    @app.callback(
        Output("twit-scat", "figure"),
        [Input("select-player", "value"), 
         Input("select-attribute", "value")]
    )
    def update_twitter_scatter(selected_players, selected_attribute):
        return sentiment.update_scatter_plot(selected_players, selected_attribute)
    

    ################################################################
    #                 code for task 3 - player comparison          #     
    ################################################################


    @app.callback(
        Output("graph-area", "children"),
        [Input("type-of-comparison", "value")]
    )
    def update_version(selected_version):
        if selected_version == "Side-by-Side":
            return comparison.side_by_side(task2data.player1, task2data.player2, task2data.player3)
        elif selected_version == "Single-Graph":
            return comparison.single_view(task2data.combine1())
        elif selected_version == "Bar Graph with Single Attribute":
            return compare_idea2
            
        

    @app.callback(
        Output("sbs-player1", "figure"),
        [Input("select-player1", "value"),
         Input("select-player1-attr1", "value"),
         Input("select-player1-attr2", "value"),
         Input("select-player1-attr3", "value"),
         Input("select-player1-attr4", "value"),]
    )
    def update_player1(selected_player, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        task2data.player1 = selected_player
        return comparison.update_side_by_side_view(task2data.player1, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)
    

    @app.callback(
        Output("sbs-player2", "figure"),
        [Input("select-player2", "value"),
         Input("select-player2-attr1", "value"),
         Input("select-player2-attr2", "value"),
         Input("select-player2-attr3", "value"),
         Input("select-player2-attr4", "value"),]
    )
    def update_player2(selected_player, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        task2data.player2 = selected_player
        return comparison.update_side_by_side_view(task2data.player2, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)
    
    @app.callback(
        Output("sbs-player3", "figure"),
        [Input("select-player3", "value"),
         Input("select-player3-attr1", "value"),
         Input("select-player3-attr2", "value"),
         Input("select-player3-attr3", "value"),
         Input("select-player3-attr4", "value"),]
    )
    def update_player3(selected_player, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        task2data.player3 = selected_player
        return comparison.update_side_by_side_view(task2data.player3, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)
    
    @app.callback(
        Output("single-view-graph", "figure"),
        [Input("select-players-single", "value"),
         Input("select-single-attr1", "value"),
         Input("select-single-attr2", "value"),
         Input("select-single-attr3", "value"),
         Input("select-single-attr4", "value"),]
    )
    def update_players(selected_players, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        task2data.single_view_players.clear()
        task2data.single_view_players = task2data.combine1()
        task2data.single_view_players = task2data.add_players_single_view(selected_players)
        

        return comparison.update_single_graph_view(task2data.single_view_players, selected_attribute1, selected_attribute2, selected_attribute3, 
                                                   selected_attribute4)


    ## Compare idea 2 ##

    @app.callback(
        Output("compare-bar", "figure"),
        [Input("player-dropdown", "value"), 
        Input("pick-attribute", "value")]
    )
    def update_comparison_chart_2(selected_players, selected_stat):
        return compare_idea2.update_compare_idea2_chart(selected_players, selected_stat)



        
    app.run_server(debug=True, dev_tools_ui=False)
