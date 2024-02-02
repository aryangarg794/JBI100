# #from typing import Self
from dash import dcc, html
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash import no_update
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import copy
from ..config import PLAYER_LIST, ATTRIBUTES_PLAYERS
import numpy as np

class TwitterSentiment(html.Div):
    def __init__(self):
        self.df_sentiment = pd.read_csv('../Data/FIFA World Cup 2022 Twitter Dataset/sentiment_mentions.csv', delimiter=',')
        self.df_tweets = pd.read_csv('../Data/FIFA World Cup 2022 Twitter Dataset/tweets_sentiment.csv', delimiter=',')
        self.df_player_combined = pd.read_csv('../Data/FIFA World Cup 2022 Player Data/stats_combined.csv', delimiter=',')
        self.df_player_valuations = pd.read_csv('../Data/Player Valuation/simple_valuations.csv', delimiter=',')

        super().__init__(
            className="sentiment_players",
            children=[
                html.H6("Sentiment analysis of Twitter Data per player"),
                make_filter_boxes(),
                dcc.Graph(
                    id='twit-scat',
                    style={'clickData' : 'event'},
                ),
                html.Div(
                    id="auxiliary-twitter-graphs",
                    children=[
                        dcc.Graph(
                            id='bar-chart',
                            figure=self.blank_fig(),
                            style={"width" : "100%"}
                        ),
                        dcc.Graph(
                            id='time-chart',
                            figure=self.blank_fig(),
                            style={"width" : "100%"}
                        ),
                    ],
                    style={"display" : "flex", "flex-direction" : "row", "width" : "100%"}
                )
            ],
            style={"color" : "white", "padding" : "10px"}
        )

    def add_valuation_column(self, df):
        
        df_copy = copy.deepcopy(df)
        
        names = df['player'].tolist()
        names_in_val = self.df_player_valuations['name'].tolist()
        temp = []

        for name in names:
            if name in names_in_val:
                value = self.df_player_valuations["market_value_in_eur_y"].loc[self.df_player_valuations["name"] == name].values[0]
                temp.append(value)
            else:
                temp.append(0.0)
        
        df_copy.loc[:, "valuation"] = temp

        return df_copy
    

    def compute_time_mentions(self, df, player):

        name_parts = player.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else name_parts[0]
        last_name = ' ' + last_name + ' '

        df = df.sort_values(by='Tweet Posted Time', ascending=True)
        df['mentions'] = df['Tweet Content'].str.lower().str.contains(last_name.lower(), regex=False)
        df['mentions'] = df['mentions'].astype(int)
        df['cumsum'] = df['mentions'].cumsum()

        df['positives'] = (df['mentions'] == 1) & (df['Sentiment'] == 'positive')
        df['positives'] = df['positives'].astype(int)

        df['neutral'] = (df['mentions'] == 1) & (df['Sentiment'] == 'neutral')
        df['neutral'] = df['neutral'].astype(int)

        df['negative'] = (df['mentions'] == 1) & (df['Sentiment'] == 'negative')
        df['negative'] = df['negative'].astype(int)

        df['cumsum_pos'] = df['positives'].cumsum()
        df['cumsum_neu'] = df['neutral'].cumsum()
        df['cumsum_neg'] = df['negative'].cumsum()
            
        return df

    
    def update_time(self, player):

        df_copy = copy.deepcopy(self.df_tweets)

        df_copy_augmented = self.compute_time_mentions(df_copy, player)

        fig = go.Figure()
        columns_to_add = {"cumsum" : "All Mentions", "cumsum_pos" : "Positive Mentions", "cumsum_neu" : "Neutral Mentions", "cumsum_neg" : "Negative Mentions"}

        for column, name in columns_to_add.items():
            fig.add_trace(go.Line(name=name,x=df_copy_augmented['Tweet Posted Time'], y=df_copy_augmented[column]))

        fig.update_layout(template="plotly_dark", showlegend=True, title_text=f"Number of Tweets about {player} over time")
        fig.update_xaxes(title_text='Time Posted', showgrid=False)
        fig.update_yaxes(title_text='Number of Mentions', range=[0, 6000])

        return fig


    
    def update_scatter_plot(self, selected_players):

        df_sentiment = copy.deepcopy(self.df_sentiment)

        if selected_players == [] or selected_players is None:
            df_player = df_sentiment
        else:
            df_player = df_sentiment[df_sentiment['player'].isin(selected_players)]

        df_combined_copy = self.add_valuation_column(self.df_player_combined)
        merged_df = pd.merge(df_player, df_combined_copy, on="player", how="inner")
        merged_df.columns = merged_df.columns.str.removesuffix("_x")
        merged_df.columns = merged_df.columns.str.removesuffix("_y")
        merged_df = merged_df.loc[:,~merged_df.columns.duplicated()].copy()
        merged_df.fillna(0)

        df_player_fw = merged_df.loc[merged_df['position'] == 'FW']
        df_player_mf = merged_df.loc[merged_df['position'] == 'MF']
        df_player_df = merged_df.loc[merged_df['position'] == 'DF']
        df_player_gk = merged_df.loc[merged_df['position'] == 'GK']

        self.fig = go.Figure()

        self.fig.add_trace(go.Scatter(
            name="Forwards",
            x=df_player_fw['mentions_count'],
            y=df_player_fw['sentiment_score'],
            mode='markers', 
            text=df_player_fw['player'] + " (" + df_player_fw['position'] + ")" + "<br>" + 
            "Country: " + df_player_fw['team'] + "<br>" +
            "Mentions: " + df_player_fw['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_fw['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_fw['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_fw['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='orange',
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Midfielders",
            x=df_player_mf['mentions_count'],
            y=df_player_mf['sentiment_score'],
            mode='markers',  
            text=df_player_mf['player'] + " (" + df_player_mf['position'] + ")" + "<br>" + 
            "Country: " + df_player_mf['team'] + "<br>" +
            "Mentions: " + df_player_mf['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_mf['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_mf['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_mf['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='blue',
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Defenders",
            x=df_player_df['mentions_count'],
            y=df_player_df['sentiment_score'],
            mode='markers',  
            text=df_player_df['player'] + " (" + df_player_df['position'] + ")" + "<br>" + 
            "Country: " + df_player_df['team'] + "<br>" +
            "Mentions: " + df_player_df['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_df['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_df['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_df['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='red',
            )
        ))

        self.fig.add_trace(go.Scatter(
            name="Goalkeepers",
            x=df_player_gk['mentions_count'],
            y=df_player_gk['sentiment_score'],
            mode='markers',  
            text=df_player_gk['player'] + " (" + df_player_gk['position'] + ")" + "<br>" + 
            "Country: " + df_player_gk['team'] + "<br>" +
            "Mentions: " + df_player_gk['mentions_count'].astype(str) + "<br>" + 
            "Positive Sentiments: " + df_player_gk['positive_tweets'].astype(str) + "<br>" +
            "Neutral Sentiments: " + df_player_gk['neutral_tweets'].astype(str) + "<br>" +
            "Negative Sentiments: " + df_player_gk['negative_tweets'].astype(str),
            hoverinfo = 'text',
            marker=dict(
                color='green',
            )
        ))

        self.fig.update_xaxes(title_text='Number of Mentions in Tweets')
        self.fig.update_yaxes(title_text='Sentiment Score')
        self.fig.update_traces(mode='markers', marker=dict(line_width=2, size=36))
        self.fig.update_layout(title_text='Tweet sentiment comparison between players', template="plotly_dark")
        


        return self.fig


    def blank_fig(self):

        self.fig = go.Figure(go.Scatter(x=[], y = []))
        self.fig.update_layout(template = "plotly_dark")
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
        self.fig.update_yaxes(title_text='Number of Tweets', range=[0, 6000])
        self.fig.update_layout(title_text='Tweet sentiment distribution of ' + player, template="plotly_dark")

        return self.fig
                                         
def make_filter_boxes():
    new_attrs = ['valuation'] + ATTRIBUTES_PLAYERS
    new_attrs.sort()
    attr_options = [{"label": i.replace("_", " ").capitalize(), "value": i} for i in new_attrs]
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
        ],
        style={"display" : "flex", "flex-direction" : "row", "flex-wrap" : "wrap", "width" : "100%", "textAlign": "float-left", "gap" : "35px", 
                  "padding" : "20px"}
    )                             
