import dash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
from yahoo_fin import stock_info
import time
import yfinance as yf
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output, State
import datetime as date, timedelta
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_market_calendars as mcal
import pandas as pd
from pmdarima.arima import auto_arima
import warnings

warnings.filterwarnings('ignore')


def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of lists
    containing rows in the csv file and its entries.
    """
    with open(csvfilename) as csvfile:
        rows = [row for row in csv.reader(csvfile)]
    return rows[1:]


def lookup(cs):
    ls = []
    for c in cs:
        ls.append({'label': c[1] + " : " + c[0], 'value': c[0]})
    return ls


def earnings(Ticker, types):
    return stock_info.get_earnings(Ticker)[types]


def news_api(ne):
    news = yf.Ticker(ne).news
    fin = {'Date': [], "News": []}
    for n in range(len(news)):
        fin["Date"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news[n]["providerPublishTime"])))
        fin["News"].append(html.A(html.P(news[n]['title']), href=news[n]['link']))
    df2 = pd.DataFrame(data=fin)
    return df2


NASQ = read_csv(r"app/static/All.csv")
opt = lookup(NASQ)
TODAY = date.date.today()
today = TODAY.strftime('%Y-%m-%d')
day = timedelta.Timedelta(days=10)
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=TODAY, end_date=TODAY + day)[:3]
early = [e.strftime('%Y-%m-%d') for e in early.index.tolist()]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\Asus\OneDrive\Desktop\credentials.json.json", scope)

# authorize the clientsheet 
client = gspread.authorize(creds)

def load_data(Ticker):
    coy = yf.Ticker(Ticker)
    data = coy.history(period="2y")
    data.reset_index()
    return data

def graph(Ticker):
    sheet = client.open(Ticker).get_worksheet(0)
    datas = sheet.get_all_records()
    return pd.DataFrame.from_dict(datas)


def predict(tick):
    sheet = client.open(tick).get_worksheet(2)
    datas = sheet.get_all_records()
    return pd.DataFrame.from_dict(datas)


def info(tick):
    sheet = client.open(tick).get_worksheet(1)
    datas = sheet.get_all_records()[:-1]
    a = datas[3]['Info']
    datas[3]['Info'] = html.A(html.P(a), href=a)
    return datas


def summary(tick):
    sheet = client.open(tick).get_worksheet(1)
    return sheet.get_all_records()[-1]['Info']


def dash_app(server):
    app = dash.Dash(server=server, routes_pathname_prefix="/", external_stylesheets=[dbc.themes.BOOTSTRAP],
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1, maximum-scale=1.2, minimum-scale=0.5'}])

    CONTENT_STYLE = {
        "padding-top": "5px",
        "padding-right": "10px",
        "padding-left": "20px"
    }

    search_bar = dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='Stock', options=opt, value="TSLA")),
            dbc.Col(
                dbc.Button(
                    "Search", id="Search", color="primary", className="ms-2", n_clicks=0
                ),
                width="auto",
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="../static/stonkzfublack.png", height="28px")),
                            dbc.Col(dbc.NavbarBrand("STOCK ANLAYSER", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    style={"textDecoration": "none"},
                ),
            ]
        ),
        color="dark",
        dark=True,
    )

    cdivs = [html.Div(id="test"),
             dbc.Row(
                 dbc.Col(search_bar, align="left"),
             ),
             dbc.Row(
                 dbc.Col(html.Div([
                     html.H4("Stock Performance:"),
                     dcc.Graph(

                         id="graph_close",
                     ),
                 ]), xs=12, sm=12, md=12, lg=12, xl=12), justify='centre'),
             dbc.Row(
                 dbc.Col(
                     html.Div([
                         html.H4('About Company'),
                         html.P(id="infom", style={"font-size": "small"})
                     ]),
                 )
             ),
             dbc.Row(
                 [

                     dbc.Col(html.Div([
                         html.Div([
                             html.H4("News:"),
                             html.Div(id='news'),
                         ]
                             , className="six columns", style={"text-align": "left", "font-size": "large"}),
                     ]), width={"size": 6}, xs=12, sm=12, md=12, lg=6, xl=6),
                     dbc.Col(html.Div([
                         html.H4('Stonkzfu.com Predictions:'),
                         dash_table.DataTable(
                             id='table',
                             style_table={"height": "auto", },
                             style_cell={
                                 "white_space": "center",
                                 "height": "auto",
                                 "font_size": "16px",
                                 'textAlign': 'center'
                             },
                             style_data={"border": "#4d4d4d", },
                             style_header={
                                 "border": "#4d4d4d",
                             },
                             style_cell_conditional=[
                                 {"if": {"column_id": c}, "textAlign": "center"}
                                 for c in ["attribute", "value"]
                             ],
                         ),
                         html.H4('General Information:'),
                         html.Div(id='gen',
                                  ),
                         html.Div([
                             html.H4("Earning:"),
                             dcc.Dropdown(
                                 id="mode",
                                 options=[
                                     {'label': 'Quarterly Results', 'value': 'quarterly_results'},
                                     {'label': 'Yearly Revenue Earnings', 'value': 'yearly_revenue_earnings'},
                                     {'label': 'Quarterly Results', 'value': 'quarterly_revenue_earnings'}
                                 ],
                                 value="quarterly_results"

                             ),
                             dash_table.DataTable(
                                 id='earn',
                                 style_table={"height": "auto", },
                                 style_cell={
                                     "white_space": "center",
                                     "height": "auto",
                                     "font_size": "16px",
                                     'textAlign': 'center'
                                 },
                                 style_data={"border": "#4d4d4d", },
                                 style_header={
                                     "border": "#4d4d4d",
                                 },
                                 style_cell_conditional=[
                                     {"if": {"column_id": c}, "textAlign": "center"}
                                     for c in ["attribute", "value"]
                                 ],
                             ),
                         ], className="six columns")

                     ]), style={'padding-top': '0.5rem'}, width={"size": 6}, xs=12, sm=12, md=12, lg=6, xl=6),

                 ]),
             ]

    content = html.Div(cdivs, style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url"), navbar,
                           content], )

    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to tell see page they are on

    @app.callback(
        Output('graph_close', 'figure'),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def lota(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            dat = load_data(value)
            MA_200 = dat.rolling(window=200).mean()
            MA_50 = dat.rolling(window=50).mean()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(dat.Close),
                                     visible=True,
                                     name="Close",
                                     showlegend=True), secondary_y=False)

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_200.Close),
                                     visible=True,
                                     name="MA_200",
                                     showlegend=True), secondary_y=False)

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_50.Close),
                                     visible=True,
                                     name="MA_50",
                                     showlegend=True,
                                     ), secondary_y=False)
            fig.add_trace(go.Bar(x=list(dat.index),
                                 y=list(dat.Volume),
                                 name="Volume", ),
                          secondary_y=True)

            fig.update_layout(
                autosize=False,
                yaxis=dict(fixedrange=True),
                xaxis=dict(
                    fixedrange=True,
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label='1m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=6,
                                 label='6m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=1,
                                 label='YTD',
                                 step='year',
                                 stepmode='todate'),
                            dict(count=1,
                                 label='1y',
                                 step='year',
                                 stepmode='backward'),
                            dict(step='all')
                        ]),

                    ),
                    type='date'
                ),
                margin=dict(
                    l=0, r=0, t=50, b=0),
                legend=dict(
                    x=0,
                    y=0.5,
                    traceorder="normal",
                )
            ),
            fig.update_yaxes(range=[0, max(list(dat.Volume)) + 0.25 * max(list(dat.Volume))], secondary_y=True,
                             visible=False)

            return fig

    @app.callback(
        [Output("table", "columns"), Output("table", "data")],
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def day(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            data = predict(value)
            columns = [{"name": i, "id": i} for i in data.columns]
            print(columns)
            t_data = data.to_dict("records")
            return columns, t_data

    @app.callback(
        Output("gen", "children"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def date(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            ans = info(value)
            fin = pd.DataFrame(data=ans)
            return dbc.Table.from_dataframe(fin, striped=True, bordered=True, hover=True, loading_state=True)

    @app.callback(
        Output("news", "children"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def date(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            ans = news_api(value)
            fin = pd.DataFrame(data=ans)
            return dbc.Table.from_dataframe(fin, striped=True, bordered=True, hover=True, loading_state=True)

    @app.callback(
        Output("infom", "children"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def get(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            return summary(value)

    @app.callback(
        [Output("earn", "columns"), Output("earn", "data")],
        Input("mode", "value"),
        State("Stock", "value")
    )
    def ear(value, values):
        if values is None:
            raise dash.exceptions.PreventUpdate
        else:
            fin = earnings(values, value)
            fin.rename(columns={'date': 'Date', 'actual': 'Actual', 'estimate': 'Estimate', 'revenue': 'Revenue',
                                'earnings': 'Earnings'}, inplace=True)
            columns = [{"name": i, "id": i} for i in fin.columns]
            t_data = fin.to_dict("records")
            return columns, t_data

    return app.server
