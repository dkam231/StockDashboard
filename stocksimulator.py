import pandas as pd
import yfinance as yf
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from datetime import datetime as dt
import pytz
from flask import Flask

tz = pytz.timezone("America/New_York")
start = tz.localize(dt(2018, 1, 1))
end = tz.localize(dt.today())

server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=['high-contrast.css'])
snp500 = pd.read_csv("constituents.csv")
symbols = snp500['Symbol'].sort_values().tolist()

df = pd.DataFrame({'c': symbols})

app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in df['c'].unique()],
        multi=True,  # Enable multi-select
        className='dropdown'
    ),
    dcc.Graph(figure={}, id='graph', className='graph'),
    html.Div(id='stock-info', className='stock-info')
])


@app.callback(Output('graph', 'figure'),
              [Input('dropdown', 'value')])
def update_output_1(values):
    if not values:
        # If no symbols are selected, return an empty figure
        return go.Figure()

    fig = go.Figure()

    for value in values:
        df = yf.download(value, start, end)
        df = df.reset_index()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Adj Close'], mode='lines', name=value))

    fig.update_layout(
        title={
            'text': "Stock Prices Over Past Two Years",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig


@app.callback(Output('stock-info', 'children'),
              [Input('dropdown', 'value')])
def update_output_2(values):
    if not values:
        # If no symbols are selected, return an empty figure
        return ''
    stock_info = []
    for value in values:
        info = yf.Ticker(value).info
        stock_info.append(
            html.Div([
                html.H3('Company Profile'),
                html.H4(info['longName']),
                html.P('Sector: ' + info['sector']),
                html.P('Industry: ' + info['industry']),
                html.P('Stock Price: $' + str(info['currentPrice'])),
                html.P('Phone: ' + info['phone']),
                html.P('Address: ' + info['address1'] + ', ' + info['city'] + ', ' + info['zip'] + ', ' + info[
                    'country']),
                html.P('Website: ' + info['website']),
                html.P('Business Summary'),
                html.P(info['longBusinessSummary'])
            ])
        )

    return stock_info


@server.route('/')
def index():
    return app.index()


@server.route('/my_dash_app')
def serve_dash_app():
    return app.index()


if __name__ == '__main__':
    server.run(debug=True)
