import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime

import yfinance


external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

stock = yfinance.Ticker('AAPL')
time = '1mo'


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])



def getMA(stock, time, date_list):
	if 'mo' in time or time=='ytd' or time=='1y':
		df = stock.history(period='2y')
	elif time=='2y' or time=='3y' or time=='4y':
		df = stock.history(period='5y')
	else:
		df = stock.history(period='10y')
	df = df.reset_index()[['Date','Open','Low','High','Close']]
	df['MA50'] = df.Close.rolling(50).mean()
	df['MA100'] = df.Close.rolling(100).mean()
	df['MA200'] = df.Close.rolling(200).mean()

	df = df.loc[(df['Date']>=date_list.min()) & (df['Date']<=date_list.max())]
	return df

df = getMA(stock, time, 
			       stock.history(period=time).reset_index()['Date'])

def getCandlestick(df):
	data = []
	data.append(go.Candlestick(x=df['Date'], open=df['Open'],
		                       high=df['High'], low=df['Low'],
		                       close=df['Close']))
	layout = {'xaxis':{'title':'Date','rangeslider':{'visible':False}},
			  'yaxis':{'title':'Price ($)'},
	          'hovermode':False}
	return {'data':data, 'layout':layout}


fig = getCandlestick(df)

contentmain = html.Div(
    [
        html.H1(stock.info['longName']),
        html.P(stock.history(period='1mo')['Close']),
        dcc.Graph(figure=fig)
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return contentmain
    elif pathname == "/page-1":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')