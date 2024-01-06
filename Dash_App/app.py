from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.pitch_and_stats import BestPlayersPitch, make_filter_boxes
from jbi100_app.views.scatterplot import Scatterplot
from jbi100_app.config import ATTRIBUTES_KEEPERS, ATTRIBUTES_PLAYERS


from dash import dcc, html, Input, Output
from dash.dependencies import ALL
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

if __name__ == '__main__':
    # Create data
    df = px.data.iris()

    # Instantiate custom views
    pitch = BestPlayersPitch()
    scatterplot1 = Scatterplot("Scatterplot 1", 'sepal_length', 'sepal_width', df)
    scatterplot2 = Scatterplot("Scatterplot 2", 'petal_length', 'petal_width', df)

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
        ],
        style={"display" : "flex", "flex-direction" : "column", "justify-content" : "center", "gap" : "50px", "background" : "white"}
    )

    # Define interactions
    @app.callback(
        Output("pitch", "figure"),
        [Input('select-countries-pitch', 'value'),
         Input('select-age-higherlower', 'value'),
         Input('select-age-input', 'value'), 
         Input('select-value-higherlower', 'value'),
         Input('select-value-input', 'value'),
         Input('select-attacker-pitch', 'value'),
         Input('select-midfielder-pitch', 'value'),
         Input('select-defender-pitch', 'value'),
         Input('select-keeper-pitch', 'value')])
    def update_pitch(selected_countries, selected_higher_lower_age, selected_age, selected_higher_lower_value, selected_value, selected_attacker_attribute,
                         selected_midfielder_attribute, selected_defender_attribute, selected_keeper_attribute):
        if selected_countries == None:
            input_countries = []
        else:
            input_countries = selected_countries

        best_forwards, best_defenders, best_midfielders, best_keeper = pitch.find_best_players(
            filters={"attack": selected_attacker_attribute, "defense": selected_defender_attribute, "goalkeeper": selected_keeper_attribute, "midfield": selected_midfielder_attribute}, 
            age_filter=[selected_higher_lower_age, selected_age], 
            value=[selected_higher_lower_value, selected_value], 
            countries=input_countries
        )
        
        return pitch.update(best_forwards, best_defenders, best_midfielders, best_keeper)
    
    # define click interaction for plot 1
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
        
    app.run_server(debug=True, dev_tools_ui=False)