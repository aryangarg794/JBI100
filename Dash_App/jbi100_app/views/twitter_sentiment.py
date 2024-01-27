from typing import Self
from dash import dcc, html
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update
import plotly.graph_objects as go
import pandas as pd
import copy
from ..config import PLAYER_LIST

class TwitterSentiment(html.Div):
    def __init__(self):
        self.df_sentiment = pd.read_csv('../Data/FIFA World Cup 2022 Twitter Dataset/sentiment_mentions.csv', delimiter=',')

        super().__init__(
            className="sentiment_players",
            children=[
                html.H6("Sentiment analysis of Twitter Data per player"),
                make_filter_boxes(),
                dcc.Graph(
                    id='twit-scat',
                    style={'clickData' : 'event'},
                    figure=self.blank_fig_task(),
                ),
                dcc.Graph(
                    id='bar-chart',
                    figure=self.blank_fig_bar(),
                ),
            ],
        )

    def blank_fig_task(self):

        color_mapping = {
            'FW': 'orange',
            'DF': 'red',
            'GK': 'green',
            'MF': 'blue',
        }

        df_sentiment = copy.deepcopy(self.df_sentiment)

        self.fig = go.Figure(go.Scatter(
            x=df_sentiment['mentions_count'],
            y=df_sentiment['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_sentiment['player'] + " (" + df_sentiment['position'] + ")" + "<br>" + 
            "Age: " + df_sentiment['age'].astype(str) + "<br>" +
            "Country: " + df_sentiment['team'] + "<br>" +
            "Mentions: " + df_sentiment['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_sentiment['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_sentiment['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_sentiment['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color=[color_mapping[position] for position in df_sentiment['position']],
                size=df_sentiment['age'] 
            )
        ))

        self.fig.update_xaxes(title_text='Number of Mentions in Tweets')
        self.fig.update_yaxes(title_text='Sentiment Score')
        self.fig.update_layout(title_text='Tweet sentiment comparison between players')

        
        return self.fig
    
    def update_scatter_player(self, selected_players):
        color_mapping = {
            'FW': 'orange',
            'DF': 'red',
            'GK': 'green',
            'MF': 'blue',
        }
        df_sentiment = copy.deepcopy(self.df_sentiment)
        df_player = df_sentiment[df_sentiment['player'].isin(selected_players)]

        self.fig = go.Figure(go.Scatter(
            x=df_player['mentions_count'],
            y=df_player['sentiment_score'],
            mode='markers',  # Set mode to 'markers' for a scatter plot
            text=df_player['player'] + " (" + df_player['position'] + ")" + "<br>" + 
            "Age: " + df_player['age'].astype(str) + "<br>" +
            "Country: " + df_player['team'] + "<br>" +
            "Mentions: " + df_player['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color=[color_mapping[position] for position in df_player['position']],
                size=df_player['age']
            )
        ))

        self.fig.update_xaxes(title_text='Number of Mentions in Tweets')
        self.fig.update_yaxes(title_text='Sentiment Score')
        self.fig.update_layout(title_text='Tweet sentiment comparison between players')


        return self.fig


    def blank_fig_bar(self):
        colors= ['red', 'gray', 'green']

        df_sentiment = copy.deepcopy(self.df_sentiment)
        variables = ['Negative Tweets', 'Neutral Tweets', 'Positive Tweets']

        self.fig = go.Figure(data=[go.Bar(
            x=variables,
            y=[0,0,0],
            marker_color = colors
        )])

        self.fig.update_xaxes(title_text='Categories of Tweets')
        self.fig.update_yaxes(title_text='Number of Tweets')
        self.fig.update_layout(title_text='Tweet sentiment distribution of ')

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
        self.fig.update_layout(title_text='Tweet sentiment distribution of ' + player)

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
                style={"display" : "flex", "flex-direction" : "column", "width" : "10%"}
            ), 
        ]
    )                             
