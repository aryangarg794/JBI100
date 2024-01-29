from jbi100_app.main import app
from jbi100_app.views.pitch_and_stats import BestPlayersPitch
from jbi100_app.views.twitter_sentiment import TwitterSentiment
from jbi100_app.config import ATTRIBUTES_KEEPERS, ATTRIBUTES_PLAYERS


from dash import dcc, html, Input, Output
from dash.dependencies import ALL
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import re

if __name__ == '__main__':

    # Instantiate custom views
    pitch = BestPlayersPitch()
    sentiment = TwitterSentiment()


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
                id="pitch-div",
                className="pitch-div-1",
                children=[
                    pitch,
                    html.Div(id="my-output")
                ],
                style={"justify-content" : "center"}
            ),
            html.Div(
                id="twit-sent",
                className="twit-sent-1",
                children=[
                    sentiment,
                    html.Div(id="my-twit-output")
                ],
                style={"justify-content" : "center"}
            )
        ],
        style={"display" : "flex", "flex-direction" : "column", "justify-content" : "center", "gap" : "50px", "background" : "white"}
    )


    ################################################################
    #                   code for task 1 - pitch plot               #     
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
            BASE_VALUES = ['goals', 'xg']
        elif position == "MF":
            BASE_VALUES = ['passes', 'assists']
        elif position == "DF":
            BASE_VALUES = ['tackles']
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
        [Input("twit-scat", "clickData")]
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
        
        
    app.run_server(debug=True, dev_tools_ui=False)
