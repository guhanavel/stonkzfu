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
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_market_calendars as mcal
import pandas as pd
import warnings
import finnhub
from pytz import timezone

warnings.filterwarnings('ignore')

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
d = timedelta.Timedelta(days=2)
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


def load_data(Ticker,tim,inter,pre):
    data = yf.download(Ticker,period=tim,interval=inter,auto_adjust=True,prepost=pre)
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
    dan = stock_info.get_data(tick, start_date=TODAY - d, end_date=TODAY).reset_index()
    if TODAY.strftime('%H:%M') > "21:00":
        data = float(dan.loc[dan["index"] == (TODAY-e).strftime('%Y-%m-%d')]["adjclose"])
        data2 = float(dan.loc[dan["index"] == (TODAY-e).strftime('%Y-%m-%d')]["adjclose"])
    else:
        data = float(dan.loc[dan["index"] == (TODAY-d).strftime('%Y-%m-%d')]["adjclose"])
        data2 = float(dan.loc[dan["index"] == (TODAY-e).strftime('%Y-%m-%d')]["adjclose"])
    status = stock_info.get_market_status()
    if status == "OPEN":
        live = stock_info.get_live_price(tick)
        return ["Open", round(live, 3), data]
    elif status == "CLOSED":
        return ["Close", round(data2, 3), round(data, 3)]
    elif status == "PRE":
        pre = stock_info.get_premarket_price(tick)
        return ["Pre-Market", round(data2, 3), round(data, 3), pre]
    elif status == "POSTPOST":
        pre = stock_info.get_postmarket_price(tick)
        return ["Post-Market", round(data2, 3), round(data, 3), pre]
    if status == "REGULAR":
        live = stock_info.get_live_price(tick)
        return ["Open", round(live, 3), data]
    else:
        return [status, round(data, 3), round(data, 2)]


def serve_layout():
    eastern = timezone('US/Eastern')
    utc_time = date.datetime.now()
    return "US TIME:" + date.datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')

def lay():
    return "Your Location Time:" + date.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
