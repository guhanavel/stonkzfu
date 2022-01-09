import csv
from yahoo_fin import stock_info
import pandas as pd
from dash import callback_context, dcc, html
import time
import yfinance as yf


def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of lists
    containing rows in the csv file and its entries.
    """
    with open(csvfilename, encoding='utf-8') as csvfile:
        rows = [row for row in csv.reader(csvfile)]
    return rows[1:]


def lookup(cs):
    def listtostring(s):
        # initialize an empty string
        str1 = " "

        # return string
        return str1.join(s)

    ls = []
    for c in cs:
        ls.append({'label': c[1] + " : " + c[0], 'value': c[0]})
    return ls


def gen(Ticker):
    dic = {'Type': ['Symbol', 'Sector', 'Industry', 'Website', 'Risk', "Next Earning Date"], "Info": []}
    info = stock_info.get_company_info(Ticker).transpose()
    infoo = info.to_dict("records")[0]
    dic["Info"].append(infoo['sector'])
    dic["Info"].append(infoo['industry'])
    dic["Info"].append(html.A(html.P(infoo['website']), href=infoo['website']))
    dic["Info"].append(infoo['overallRisk'])
    dic["Info"].append(stock_info.get_next_earnings_date(Ticker).strftime("%Y-%m-%d %H:%M:%S"))

    return dic


def su(Ticker):
    info = list(stock_info.get_company_info(Ticker).iloc[[5]]["Value"])
    return info[0]


def summary(st):
    count = 0
    index = []
    for s in range(len(st)):
        if st[s] == ".":
            count += 1
            index.append(s)
    if count <= 3:
        return st
    else:
        return st[:index[1] + 1] + st[index[-3] + 1:index[-1] + 1]


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


def load_data(Ticker):
    coy = yf.Ticker(Ticker)
    data = coy.history(period="max")
    data.reset_index()
    return data