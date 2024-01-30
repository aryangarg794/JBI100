from typing import Self
from dash import dcc, html
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update
import plotly.graph_objects as go
import pandas as pd
import copy
from ..config import PLAYER_LIST, ATTRIBUTES_PLAYERS

class TwitterSentiment(html.Div):
    def __init__(self):
        self.df_sentiment = pd.read_csv('../Data/FIFA World Cup 2022 Twitter Dataset/sentiment_mentions.csv', delimiter=',')
        self.df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')

        super().__init__(
            className="sentiment_players",
            children=[
                html.H6("Sentiment analysis of Twitter Data per player"),
                make_filter_boxes(),
                dcc.Graph(
                    id='twit-scat',
                    style={'clickData' : 'event'},
                ),
                dcc.Graph(
                    id='bar-chart',
                    figure=self.blank_fig(),
                ),
            ],
        )

    
    def update_scatter_plot(self, selected_players, chosen_attribute='age'):

        df_sentiment = copy.deepcopy(self.df_sentiment)

        if selected_players == [] or selected_players is None:
            df_player = df_sentiment
        else:
            df_player = df_sentiment[df_sentiment['player'].isin(selected_players)]

        attribute_max = self.df_player_combined[chosen_attribute].max()
        attribute_min = self.df_player_combined[chosen_attribute].min()

        self.df_player_combined['size'] = self.df_player_combined[chosen_attribute].apply(lambda value: ((value - attribute_min)/(attribute_max-attribute_min)) * 30)

        sizeref = 2.*max(self.df_player_combined['size'])/(100**2)

        df_player_fw = df_player.loc[df_player['position'] == 'FW']
        df_player_mf = df_player.loc[df_player['position'] == 'MF']
        df_player_df = df_player.loc[df_player['position'] == 'DF']
        df_player_gk = df_player.loc[df_player['position'] == 'GK']

        self.fig = go.Figure()

        self.fig.add_trace(go.Scatter(
            name="Forwards",
            x=df_player_fw['mentions_count'],
            y=df_player_fw['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_player_fw['player'] + " (" + df_player_fw['position'] + ")" + "<br>" + 
            "Age: " + df_player_fw['age'].astype(str) + "<br>" +
            "Country: " + df_player_fw['team'] + "<br>" +
            "Mentions: " + df_player_fw['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_fw['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_fw['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_fw['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='orange',
                size=self.df_player_combined['size'].tolist()
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Midfielders",
            x=df_player_mf['mentions_count'],
            y=df_player_mf['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_player_mf['player'] + " (" + df_player_mf['position'] + ")" + "<br>" + 
            "Age: " + df_player_mf['age'].astype(str) + "<br>" +
            "Country: " + df_player_mf['team'] + "<br>" +
            "Mentions: " + df_player_mf['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_mf['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_mf['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_mf['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='blue',
                size=self.df_player_combined['size'].tolist()
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Defenders",
            x=df_player_df['mentions_count'],
            y=df_player_df['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_player_df['player'] + " (" + df_player_df['position'] + ")" + "<br>" + 
            "Age: " + df_player_df['age'].astype(str) + "<br>" +
            "Country: " + df_player_df['team'] + "<br>" +
            "Mentions: " + df_player_df['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_df['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_df['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_df['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='red',
                size=self.df_player_combined['size'].tolist()
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Goalkeepers",
            x=df_player_gk['mentions_count'],
            y=df_player_gk['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_player_gk['player'] + " (" + df_player_gk['position'] + ")" + "<br>" + 
            "Age: " + df_player_gk['age'].astype(str) + "<br>" +
            "Country: " + df_player_gk['team'] + "<br>" +
            "Mentions: " + df_player_gk['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_gk['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_gk['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_gk['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='green',
                size=self.df_player_combined['size'].tolist()
            )
        ))

        self.fig.update_xaxes(title_text='Number of Mentions in Tweets')
        self.fig.update_yaxes(title_text='Sentiment Score')
        self.fig.update_traces(mode='markers', marker=dict(sizemode='area', sizeref=sizeref, line_width=2))
        self.fig.update_layout(title_text='Tweet sentiment comparison between players', template="plotly_dark")
        


        return self.fig


    def blank_fig(self):

        self.fig = go.Figure(go.Scatter(x=[], y = []))
        self.fig.update_layout(template = None)
        self.fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
        self.fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

        return self.fig
    
    def update_fig_bar(self, player, positive_tweets, neutral_tweets, negative_tweets):
        colors=['red', 'gray', 'green']
        variables = ['Negative Tweets', 'Neutral Tweets', 'Positive Tweets']
        values = [negative_tweets, neutral_tweets, positive_tweets]

        self.fig = go.Figure(data=[go.Bar(
            x=variables,
            y=values,
            marker_color = colors
        )])

        self.fig.update_xaxes(title_text='Categories of Tweets')
        self.fig.update_yaxes(title_text='Number of Tweets')
        self.fig.update_layout(title_text='Tweet sentiment distribution of ' + player, template="plotly_dark")

        return self.fig
                                         
def make_filter_boxes():
    
    return html.Div(
        id="control-twitter-card",
        children=[
            html.Div(
                id="player-picker",
                children=[
                html.Label("Player"),
                dcc.Dropdown(
                    id="select-player",
                    options=[{"label": i, "value": i} for i in PLAYER_LIST],
                    multi=True,
                    value=None,
                    searchable=True,
                    placeholder="Select Players", 
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
            ), 
            html.Div(
                id="attribute-picker",
                children=[
                html.Label("Size Attribute"),
                dcc.Dropdown(
                    id="select-attribute",
                    options=[{"label": i.replace("_", " ").capitalize(), "value": i} for i in ATTRIBUTES_PLAYERS],
                    multi=False,
                    value='age',
                    searchable=True,
                    placeholder="Select Attribute (Keeper Attributes Excluded)", 
                    style={"margin-top" : "5px"}
                ),
                ],
                style={"display" : "flex", "flex-direction" : "column", "width" : "20%"}
            ), 
        ],
        style={"display" : "flex", "flex-direction" : "row", "flex-wrap" : "wrap", "width" : "100%", "textAlign": "float-left", "gap" : "35px", 
                  "padding" : "20px"}
    )                             
