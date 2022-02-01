import dash
import gspread
import pytz
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
from datetime import date as dt
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_market_calendars as mcal
import pandas as pd
import warnings

warnings.filterwarnings('ignore')
import finnhub
from pytz import timezone
import dash_table
import dash_daq as daq
import numpy as np
from GoogleNews import GoogleNews

warnings.filterwarnings('ignore')

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name(r"app/static/credentials.json.json", scope)

# authorize the clientsheet
client = gspread.authorize(creds)

TODAY = date.date.today()
today = TODAY.strftime('%Y-%m-%d')
day = timedelta.Timedelta(days=10)
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=TODAY, end_date=TODAY + day)[:3]
early = [e.strftime('%Y-%m-%d') for e in early.index.tolist()]
d = timedelta.Timedelta(days=4)
e = timedelta.Timedelta(days=1)
hour = timedelta.Timedelta(hours=7)

finnhub_client = finnhub.Client(api_key="c7l6tpqad3i9ji44hd40")


def read_csv(csvfilename, encoding='utf-8'):
    """
    Reads a csv file and returns a list of lists
    containing rows in the csv file and its entries.
    """
    with open(csvfilename, encoding='utf-8') as csvfile:
        rows = [row for row in csv.reader(csvfile)]
    return rows[1:]


def lookup(cs):
    ls = []
    for c in cs:
        ls.append({'label': c[1] + " : " + c[0], 'value': c[0]})
    return ls


def newp(cs):
    ls = []
    for c in cs:
        ls.append({'label': c[1] + " : " + c[0], 'value': dcc.Link(href='/das/?val=' + str(c[0]))})


def sy_name(cs):
    di = {}
    for c in cs:
        di[c[0]] = c[1]
    return di


def earnings(Ticker, types):
    return stock_info.get_earnings(Ticker)[types]


NASQ = read_csv(r"app/static/AAll.csv")
sy = sy_name(NASQ)


def news_api(tick, start, end):
    dy = []
    googlenews = GoogleNews(lang='en', region='US', start=start, end=end)
    googlenews.search(sy[tick] + " stock")
    a = googlenews.result()
    for n in a:
        dy.append(html.Div(dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5(n['title'], style={"font-size": "small"}),
                        dbc.Button("View", href=n['link'])

                    ]

                ),
            ], style={"width": "18rem", }, ), ))
    return dy


def load_data(Ticker, tim, inter, pre):
    data = yf.download(Ticker, period=tim, interval=inter, auto_adjust=True, prepost=pre)
    data.reset_index()
    return data


def graph(Ticker):
    sheet = client.open(Ticker).get_worksheet(0)
    datas = sheet.get_all_records()
    return pd.DataFrame.from_dict(datas)


def predict(tick):
    dat = []
    sheet = client.open(tick).get_worksheet(2)
    datas = sheet.get_all_records()
    dat.append(datas[-3])
    dat.append(datas[-2])
    dat.append(datas[-1])
    return pd.DataFrame.from_dict(dat)


def info(tick):
    sheet = client.open(tick).get_worksheet(1)
    datas = sheet.get_all_records()[:-1]
    a = datas[3]['Info']
    datas[3]['Info'] = html.A(html.P(a), href=a)
    return datas


def summary(tick):
    sheet = client.open(tick).get_worksheet(1)
    return sheet.get_all_records()[-1]['Info']


TODAY = date.date.today()
day = timedelta.Timedelta(days=90)
star = TODAY - day
en = TODAY + day


def even():
    even = []
    for fin in finnhub_client.ipo_calendar(_from=star.strftime('%Y-%m-%d'), to=en.strftime('%Y-%m-%d'))['ipoCalendar']:
        even.append({'title': str(fin['name']),
                     'start': fin['date'],
                     'end': fin['date'],
                     'url': '/das'})
    return even


def get_events():
    sheet = client.open("cal").get_worksheet(0)
    data = sheet.get_all_records()
    data += even()
    return data


def live_prices(tick):
    dan = yf.download(tick, period="5d")
    status = stock_info.get_market_status()
    yes = float(dan[-1:].Close)  # yesterday
    yyes = float(dan[-2:-1].Close)  # previous
    if status == "OPEN":
        live = stock_info.get_live_price(tick)
        return ["Open", yyes,round(live, 3)]
    elif status == "CLOSED":
        pre = stock_info.get_postmarket_price(tick)
        return ["Close; After-Market", round(yyes, 3), round(yes, 3), pre]
    elif status == "PRE":
        pre = stock_info.get_premarket_price(tick)
        return ["Pre-Market", round(yes, 3), pre]
    elif status == "POSTPOST":
        pre = stock_info.get_postmarket_price(tick)
        return ["Post-Market", round(yyes, 3), round(yes, 3), pre]
    if status == "REGULAR":
        live = stock_info.get_live_price(tick)
        return ["Open", yyes, round(live, 3)]
    else:
        return [status[:3], round(yes, 3), round(yes, 3)]


def stat():
    status = stock_info.get_market_status()
    if status == "OPEN":
        return "Open"
    elif status == "CLOSED":
        return "Close"
    elif status == "PRE":
        return "Pre-Market"
    elif status == "POSTPOST":
        return "Post-Market"
    if status == "REGULAR":
        return "Open"
    else:
        return status[:3]


def serve_layout():
    eastern = timezone('US/Eastern')
    utc_time = date.datetime.now()
    return "US TIME:" + date.datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')


def lay():
    return "Your Location Time:" + date.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def recom(tick):
    mn = {"strongsell": 1, "sell": 3, "hold": 5, "buy": 7, "stongbuy": 9}
    dic = finnhub_client.recommendation_trends(tick)[-1]
    perid = dic.pop('period')
    dic.pop('symbol')
    val_list = list(dic.values())
    key_list = list(dic.keys())
    return mn[key_list[val_list.index(max(dic.values()))]], perid


def sm(tick):
    sm = finnhub_client.stock_social_sentiment(tick)
    red = pd.DataFrame.from_dict(sm["reddit"])
    twi = pd.DataFrame.from_dict(sm["twitter"])
    red["atTime"] = pd.DatetimeIndex(red.atTime, tz='UTC').tz_convert("US/Eastern")
    twi["atTime"] = pd.DatetimeIndex(twi.atTime, tz='UTC').tz_convert("US/Eastern")
    red["s_add"] = red.score[::-1].cumsum(axis=0)
    twi["s_add"] = twi.score[::-1].cumsum(axis=0)
    red = red.set_index("atTime")
    twi = twi.set_index("atTime")
    data = [twi["s_add"], red["s_add"], twi["score"], red["score"], red["mention"], twi["mention"]]
    headers = ["red_add", "twi_add", "twi_score", "red_score", "red_mention", "twi_mention"]
    df = pd.concat(data, axis=1, keys=headers).fillna(0)
    df["overall"] = df["twi_score"] + df["red_score"]
    df["o_sum"] = df["overall"].cumsum(axis=0)
    df["mention"] = df["red_mention"] + df["twi_mention"]
    return df


def prices(cs):
    dy = ["Status:" + stat() + " ", ]
    for a in cs:
        try:
            state = stock_info.get_live_price(a)
        except:
            state = 0
        dy.append(str(a) + ":$" + str(round(state, 2)) + "USD  ")
    return dy


def gain():
    gain = stock_info.get_day_gainers()[:10]
    data = [gain["Symbol"], gain["Name"], gain["Price (Intraday)"], gain["Change"], gain["% Change"]]
    headers = ["Symbol", "Name", "Price", "Change", "% Change"]
    df = pd.concat(data, axis=1, keys=headers)
    return df


def lose():
    gain = stock_info.get_day_losers()[:10]
    data = [gain["Symbol"], gain["Name"], gain["Price (Intraday)"], gain["Change"], gain["% Change"]]
    headers = ["Symbol", "Name", "Price", "Change", "% Change"]
    df = pd.concat(data, axis=1, keys=headers)
    return df


def active():
    gain = stock_info.get_day_most_active()[:10]
    data = [gain["Symbol"], gain["Name"], gain["Price (Intraday)"], gain["Change"], gain["% Change"]]
    headers = ["Symbol", "Name", "Price", "Change", "% Change"]
    df = pd.concat(data, axis=1, keys=headers)
    return df


T = read_csv(r"app/static/Top25.csv")


def stock_cards(tick):
    dy = []
    for t in tick[:6]:
        try:
            dat = load_data(t[0], '1mo', '1d', False)

            def what():
                if live_prices(t[0])[2] > dat.Close.iloc[0]:
                    return 'green'
                elif live_prices(t[0])[2] < dat.Close.iloc[0]:
                    return 'red'
                else:
                    return 'grey'

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(dat.Close),
                                     showlegend=False,
                                     line=dict(color=what(), width=1)))
            fig.update_layout(
                autosize=False,
                height=200,
                width=200,
                xaxis=dict(fixedrange=True),
                yaxis=dict(fixedrange=True),
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            ),
            fig2 = go.Figure()
            fig2.add_trace(go.Indicator(mode="number+delta", value=round(live_prices(t[0])[2], 2),
                                        number={'valueformat': 'f', 'suffix': "USD", "font": {"size": 20}},
                                        delta={'reference': live_prices(t[0])[1], 'relative': True,
                                               'position': "bottom"},
                                        align="left", ), ),
            fig2.update_layout(
                autosize=False,
                height=100,
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            ),
            dy.append(dbc.Col(dbc.Card(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.CardHeader(
                                    html.Div(children=[dcc.Graph(figure=fig)]),
                                ),
                                width=7,
                            ),
                            dbc.Col(
                                dbc.CardBody(
                                    [html.H5(str(t[1]) + ":" + str(t[0]), className="card-title",style={"font-size":"medium"}),
                                     html.Div(children=[dcc.Graph(figure=fig2, config={
                                         'displayModeBar': False
                                     }, style={'height': 'auto', 'width': 'auto'})]),
                                     html.A(dbc.Button("View"), href='/das/?val=' + str(t[0]))
                                     ]
                                ),
                                width=5
                            ),
                        ],
                        className="g-0 d-flex align-items-center",
                    ), ],
                className="mb-3",
                style={"maxWidth": "540px"},
            ),xs=12, sm=12, md=12, lg=6, xl=6))
        except:
            pass
    return dy
