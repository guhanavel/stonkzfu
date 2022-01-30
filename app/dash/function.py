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
import datetime as date,timedelta
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

def sy_name(cs):
    di = {}
    for c in cs:
        di[c[0]] = c[1]
    return di


def earnings(Ticker, types):
    return stock_info.get_earnings(Ticker)[types]

NASQ = read_csv(r"app/static/AAll.csv")
sy = sy_name(NASQ)

def news_api(tick,start,end):
    dy = []
    googlenews = GoogleNews(lang='en', region='US', start=start, end=end)
    googlenews.search(sy[tick]+ " stock")
    a = googlenews.result()
    for n in a:
        dy.append(html.Div(dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5(n['title'],style={"font-size":"small"}),
                        dbc.Button("View", href=n['link'])

                        ]

                ),
                ],style={"width": "18rem",},),))
    return dy


def load_data(Ticker,tim,inter,pre):
    data = yf.download(Ticker,period=tim,interval=inter,auto_adjust=True,prepost=pre)
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
    dan = yf.download(tick,period="5d")
    status = stock_info.get_market_status()
    yes = float(dan[-1:].Close) #yesterday
    yyes = float(dan[-2:-1].Close) #previous
    if status == "OPEN":
        live = stock_info.get_live_price(tick)
        return ["Open", round(live, 3), yyes]
    elif status == "CLOSED":
        pre = stock_info.get_postmarket_price(tick)
        return ["Close; After-Market", round(yyes, 3),round(yes, 3),pre]
    elif status == "PRE":
        pre = stock_info.get_premarket_price(tick)
        return ["Pre-Market", round(yes, 3), pre]
    elif status == "POSTPOST":
        pre = stock_info.get_postmarket_price(tick)
        return ["Post-Market", round(yyes, 3), round(yes, 3), pre]
    if status == "REGULAR":
        live = stock_info.get_live_price(tick)
        return ["Open", round(live, 3), yyes]
    else:
        return [status, round(yes, 3), round(yes, 3)]


def serve_layout():
    eastern = timezone('US/Eastern')
    utc_time = date.datetime.now()
    return "US TIME:" + date.datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')

def lay():
    return "Your Location Time:" + date.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def recom(tick):
    mn = {"strongsell":1,"sell":3,"hold":5,"buy":7,"stongbuy":9}
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
    red["atTime"] = pd.DatetimeIndex(red.atTime,tz='UTC').tz_convert("US/Eastern")
    twi["atTime"] = pd.DatetimeIndex(twi.atTime,tz='UTC').tz_convert("US/Eastern")
    red["s_add"] = red.score[::-1].cumsum(axis=0)
    twi["s_add"]= twi.score[::-1].cumsum(axis=0)
    red =  red.set_index("atTime")
    twi = twi.set_index("atTime")
    data = [twi["s_add"],red["s_add"],twi["score"],red["score"],red["mention"],twi["mention"]]
    headers = ["red_add","twi_add","twi_score","red_score","red_mention","twi_mention"]
    df = pd.concat(data, axis=1,keys=headers).fillna(0)
    df["overall"] = df["twi_score"]+df["red_score"]
    df["o_sum"] = df["overall"].cumsum(axis=0)
    df["mention"] = df["red_mention"]+df["twi_mention"]
    return df

