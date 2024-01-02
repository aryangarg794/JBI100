from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.pitch_and_stats import BestPlayersPitch, make_filter_boxes
from jbi100_app.views.scatterplot import Scatterplot

from dash import html, Input, Output
import plotly.express as px


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
                    pitch
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
    def update_countries(selected_countries, selected_higher_lower_age, selected_age, selected_higher_lower_value, selected_value, selected_attacker_attribute,
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
        

    @app.callback(
        Output(scatterplot2.html_id, "figure"), [
        Input("select-color-scatter-2", "value"),
        Input(scatterplot1.html_id, 'selectedData')
    ])
    def update_scatter_2(selected_color, selected_data):
        return scatterplot2.update(selected_color, selected_data)

    pitch.find_best_players()
    app.run_server(debug=True, dev_tools_ui=False)