from jbi100_app.main import app
from jbi100_app.views.pitch_and_stats import BestPlayersPitch
from jbi100_app.views.twitter_sentiment import TwitterSentiment
from jbi100_app.views.player_comparison import PlayerComparison
from jbi100_app.views.pcp_task1 import PCPTask1
from jbi100_app.views.compare_idea2 import CompareIdea2
from jbi100_app.config import ATTRIBUTES_KEEPERS, ATTRIBUTES_PLAYERS


import pandas as pd
import re

from dash import dcc, html, Input, Output
from dash.dependencies import ALL
import plotly.graph_objects as go
import plotly.express as px


"""
Class Task2Data
inputs - none
class vars 
- player1:str (the player first player in a side-by-side view)
- player2:str (the second player in a side-by-side view)
- player3:str (the second player in a side-by-side view)

- single_view_players:list (list which is used for the single graph view)
- bar_chart_players:list (list to store players for bar chart view (not used/implemented))

the function of this class is to keep a sort of pseudo-global state, with which when you switch between the side-by-side TO the single view your 
players are preserved (the other way is not implemented and also there is no connection to the bar chart as of yet)

"""
class Task2Data():
    
    def __init__(self):
        self.player1 = "Harry Kane"
        self.player2 = "Lionel Messi"
        self.player3 = "Jude Bellingham"

        self.single_view_players = []
        self.bar_view_players = []

    # add each player from side-by-side to the single graph list
    def combine1(self):
        self.single_view_players.append(self.player1)
        self.single_view_players.append(self.player2)
        self.single_view_players.append(self.player3)

        return list(set(self.single_view_players))
    
    # similar as combine1 but for the bar graph
    def combine2(self):
        self.bar_view_players.append(self.player1)
        self.bar_view_players.append(self.player2)
        self.bar_view_players.append(self.player3)

        return list(set(self.bar_view_players))
    
    # given a list of players we add them to the single graph list
    def add_players_single_view(self, players):
        for player in players:
            self.single_view_players.append(player)

        return list(set(self.single_view_players))
    
    # similar as function above but for the bar graph list
    def add_players_bar(self, players):
        for player in players:
            self.bar_view_players.append(player)

        return list(set(self.bar_view_players))



if __name__ == '__main__':

    # Instantiate custom views and data classes
    pitch = BestPlayersPitch()
    sentiment = TwitterSentiment()
    comparison = PlayerComparison()
    compare_idea2 = CompareIdea2()
    pcp = PCPTask1()

    task2data = Task2Data()


    ################################################################
    #                  vis overall display code                    #     
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
        style={"display" : "flex", "flex-direction" : "column", "justify-content" : "center", "background" : "#111111"}
    )

    ################################################################
    #            code for task 1 - relation between factors        #     
    ################################################################

    """
    This function is designed switch between the player attribute filter or keeper attribute filters based on user choice
    """
    @app.callback(
        Output("filter-pcp-plot", "children"),
        [Input("keepers-or-players", "value")]
    )
    def update_version(selected_version):
        # return the correct div based on type chosen
        match selected_version:
            case "Player Attributes":
                return pcp.make_attribute_selection_outfield()
            case "Keeper Attributes":
                return pcp.make_attribute_selection_keepers()
    

    """
    This function is designed to alter the pcp graph based on the attributes selected in the 4 attribute boxes made for the pcp graph
    """
    @app.callback(
        Output("pcp-plot", "figure"),
        [Input("pcp-attribute-1", "value"),
         Input("pcp-attribute-2", "value"), 
         Input("pcp-attribute-3", "value"),
         Input("pcp-attribute-4", "value")]
    )
    def update_pcp_plot(selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        return pcp.update_pcp(selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)
    
    """
    This function returns the scatter plot based on the attributes selected in the first 2 attribute boxes
    """
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

    """
    This function gets the selected attributes and the respective slider values, computes the best_players df for each position and then passes them to the 
    update pitch graph function 
    """
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
        
        # if no country is selected then return empty list (this is coupled with the update function checking len != 0)
        if selected_countries == None:
            input_countries = []
        else:
            input_countries = selected_countries

        # return the best_players df based on the attributes and slider values
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
        
        # update the pitch based on dfs
        return pitch.update(best_forwards, best_defenders, best_midfielders, best_keeper)
    

    """
    This function updates the bottom (attribute) filter boxes so that the sliders are correct and can be used properly
    """
    @app.callback(
            Output("attributes-and-sliders", "children"), 
            [Input('select-attacker-pitch', 'value'),
            Input('select-midfielder-pitch', 'value'),
            Input('select-defender-pitch', 'value'),
            Input('select-keeper-pitch', 'value'),])
    def on_attribute_change(selected_attacker_attribute, selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute,):
        return pitch.make_filter_boxes_bottom(selected_attacker_attribute, selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute)
    
    """
    This function on click returns the information table regarding the specific player that the user clicked on
    """
    @app.callback(
            Output("pitch-player-graph", "figure"), 
            [Input("pitch", 'clickData'),
             Input("select-player-attrs-dropdown", 'value')])
    def on_player_click_graph(click_data, selected_attributes):
        # get the player name from the click data
        player = click_data['points'][0]['text']
        # get the player position from the custom data
        position = click_data['points'][0]['customdata'][1]
        return pitch.update_player(player, position, selected_attributes)
    
    """
    This function uses the column in the filter box adjacent to the table and then adjusts the filter box based on the position of the player clicked
    """
    @app.callback(
            Output("left-column-player", "children"), 
            [Input("pitch", 'clickData')])
    def on_player_click(click_data):
        # get player position and name from clickdata
        player = click_data['points'][0]['text']
        position = click_data['points'][0]['customdata'][1]

        
        df_vals = pd.read_csv("../Data/Player Valuation/simple_valuations.csv")
        
        # get val of player
        value = df_vals["market_value_in_eur_y"].loc[df_vals['name'] == player].values[0]

        # based on position chosen we select an INITIAL array of attributes that might be interesting to the user
        match position:
            case "FW":
                BASE_VALUES = ['goals', 'xg', 'pens_made', 'npxg_per_shot', 'minutes', 'dribbles_completed', 'dribbles', 'miscontrols', 'passes_received', 'shots_on_target']
            case "MF":
                BASE_VALUES = ['passes', 'assists', 'aerials_won', 'passes_completed', 'passes_total_distance', 'passes_short', 'passes_medium', 'crosses_into_penalty_area', 'through_balls']
            case "DF":
                BASE_VALUES = ['tackles', 'interceptions', 'tackles_interceptions', 'blocked_shots', 'blocked_passes', 'blocks', 'dribbled_past', 'tackles_won']
            case "GK":
                BASE_VALUES = ['gk_goals_against', 'gk_saves']

        # for goal keepers we use a different attribute list so we adjust dropdown options based on that
        if position == 'GK':
            div = html.Div(
            id="select-player-attrs",
            children=[
                html.H2(f"{player} ({position}) has value €{value}"),
                html.Label("The greener the better the stat"),
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
            style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "padding" : "20px"}
            )
        else:
            div = html.Div(
            id="select-player-attrs",
            children=[
                html.H2(f"{player} ({position}) has value €{value}"),
                html.Label("The greener the better the stat"),
                dcc.Dropdown(
                    id="select-player-attrs-dropdown",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                    multi=True,
                    value=BASE_VALUES,
                    searchable=True,
                    clearable=False,
                    placeholder="Select attributes to display",
                    style={"margin-top" : "5px", "width" : "100%"}
                ),
            ],
            style={"display" : "flex", "flex-direction" : "column", "width" : "100%", "padding" : "20px"}
            )
        return div




    ################################################################
    #           code for task 4 - twitter sentiment analysis       #     
    ################################################################


    """
    This function updates the bar chart of the twitter-sentiment scatter plot based on the hover data used 
    """
    @app.callback(
        Output("bar-chart", "figure"),
        [Input("twit-scat", "hoverData")]
    )
    def update_bar_chart(click_data):
        # we use regex to get the right information from the hover label
        selected_player = click_data['points'][0]['text'].split('<br>')[0]
        player = re.sub(r'\([^)]*\)', '', selected_player).strip()
        positive_tweets = int(click_data['points'][0]['text'].split('<br>')[-3].split(': ')[1])
        neutral_tweets = int(click_data['points'][0]['text'].split('<br>')[-2].split(': ')[1])
        negative_tweets = int(click_data['points'][0]['text'].split('<br>')[-1].split(': ')[1])

        return sentiment.update_fig_bar(player, positive_tweets, neutral_tweets, negative_tweets)
    
    """
    This function uses the select player dropdown to highlight certain players on the scatter plot
    """
    @app.callback(
        Output("twit-scat", "figure"),
        [Input("select-player", "value")]
    )
    def update_twitter_scatter(selected_players):
        return sentiment.update_scatter_plot(selected_players)
    

    """
    This function updates the time-series chart based on user hover
    """
    @app.callback(
        Output("time-chart", "figure"),
        [Input("twit-scat", "hoverData")]
    )
    def update_line(click_data):
        # get the needed information using regex from the hover label data
        selected_player = click_data['points'][0]['text'].split('<br>')[0]
        player = re.sub(r'\([^)]*\)', '', selected_player).strip()
        
        return sentiment.update_time(player)

    ################################################################
    #                 code for task 3 - player comparison          #     
    ################################################################

    """
    This function uses the type of comparison dropdown to return the selected view
    """
    @app.callback(
        Output("graph-area", "children"),
        [Input("type-of-comparison", "value")]
    )
    def update_version(selected_version):
        # return the right view based on selection
        match selected_version:
            case "Side-by-Side":
                return comparison.side_by_side(task2data.player1, task2data.player2, task2data.player3) 
            case "Single-Graph":
                return comparison.single_view(task2data.combine1())
            case "Bar Graph with Single Attribute":
                return compare_idea2
            
    """
    This function updates player 1 of the side-by-side view based on the attributes selected 
    """
    @app.callback(
        Output("sbs-player1", "figure"),
        [Input("select-player1", "value"),
         Input("select-player1-attr1", "value"),
         Input("select-player1-attr2", "value"),
         Input("select-player1-attr3", "value"),
         Input("select-player1-attr4", "value"),]
    )
    def update_player1(selected_player, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        # update player 1 in the global data class
        task2data.player1 = selected_player
        return comparison.update_side_by_side_view(task2data.player1, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4)

    """
    This function updates player 2 of the side-by-side view based on the attributes selected 
    """   
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

    """
    This function updates player 3 of the side-by-side view based on the attributes selected 
    """
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

    """
    This function updates the single graph view, by taking the list of players given y the dropdown and the attributes chosen by the user
    """
    @app.callback(
        Output("single-view-graph", "figure"),
        [Input("select-players-single", "value"),
         Input("select-single-attr1", "value"),
         Input("select-single-attr2", "value"),
         Input("select-single-attr3", "value"),
         Input("select-single-attr4", "value"),]
    )
    def update_players(selected_players, selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4):
        # clear the list so that we dont make the list too large and make it so that we can remove players also
        task2data.single_view_players.clear()

        # add the players from the side-by-side view (this also means that these players cannot be removed since they are set and cannot be unset)
        # this can be offset by using plotly's inbuilt selection system
        task2data.single_view_players = task2data.combine1()

        # add the players chosen from the dropdown
        task2data.single_view_players = task2data.add_players_single_view(selected_players)
        
        return comparison.update_single_graph_view(task2data.single_view_players, selected_attribute1, selected_attribute2, selected_attribute3, 
                                                   selected_attribute4)


    """
    This function updates the bar chart view for player comparison based on the attributes and the players chosen
    """
    @app.callback(
        Output("compare-bar", "figure"),
        [Input("player-dropdown", "value"), 
        Input("pick-attribute", "value")]
    )
    def update_comparison_chart_2(selected_players, selected_stat):
        return compare_idea2.update_compare_idea2_chart(selected_players, selected_stat)



        
    app.run_server(debug=True, dev_tools_ui=False)
