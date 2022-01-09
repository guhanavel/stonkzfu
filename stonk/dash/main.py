import dash
import csv
from yahoo_fin import stock_info
import pandas as pd
from dash import callback_context, dcc, html
import time
import yfinance as yf
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output, State
import datetime as date, timedelta
import plotly.graph_objs as go
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
    with open(csvfilename, encoding='utf-8') as csvfile:
        rows = [row for row in csv.reader(csvfile)]
    return rows[1:]


def lookup(cs):
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


NASQ = read_csv(r"\static\constituents_csv.csv")
opt = lookup(NASQ)
TODAY = date.date.today()
today = TODAY.strftime('%Y-%m-%d')
day = timedelta.Timedelta(days=10)
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=TODAY, end_date=TODAY + day)[:3]
early = [e.strftime('%Y-%m-%d') for e in early.index.tolist()]
predictions = {}


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
                 [
                     dbc.Col(html.Div([
                         dcc.Graph(

                             id="col",
                         ),
                     ]), xs=6, sm=6, md=6, lg=3, xl=3),
                     dbc.Col(html.Div([
                         dcc.Graph(

                             id="open",
                         ),
                     ]), xs=6, sm=6, md=6, lg=3, xl=3),
                     dbc.Col(html.Div([
                         dcc.Graph(

                             id="high",
                         ),
                     ]), xs=6, sm=6, md=6, lg=3, xl=3),

                     dbc.Col(html.Div([
                         dcc.Graph(

                             id="low",
                         ),
                     ]), xs=6, sm=6, md=6, lg=3, xl=3),

                 ]
             ),

             dbc.Row(
                 dbc.Col(html.Div([
                     dcc.Graph(

                         id="vol",
                     ),
                 ]), xs=12, sm=12, md=12, lg=12, xl=12), justify='centre'),
             dbc.Row(
                 dbc.Col(html.Div([
                     html.H4("Stock Performance:"),
                     dcc.Graph(

                         id="graph_close",
                     ),
                 ]), xs=12, sm=12, md=12, lg=12, xl=12), justify='centre'),
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
                         html.H4('Predictions:'),
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
             dbc.Row(
                 dbc.Col(
                     html.Div([
                         html.H4('About Company'),
                         html.P(id="infom")
                     ]),
                 )
             )
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
            data = load_data(value).reset_index()
            data = data[["Date", "Close", "Volume"]]
            MA_200 = dat.rolling(window=200).mean()
            MA_50 = dat.rolling(window=50).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(dat.Close),
                                     visible=True,
                                     name="Close",
                                     showlegend=True))

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_200.Close),
                                     visible=True,
                                     name="MA_200",
                                     showlegend=True))

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_50.Close),
                                     visible=True,
                                     name="MA_50",
                                     showlegend=True))

            fig.update_layout(
                autosize=False,
                yaxis=dict(fixedrange=False),
                xaxis=dict(
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
                    rangeslider=dict(
                        visible=True
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
            )

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
            def predict(Ticker):
                df = load_data(Ticker)
                df_close = df['Close']
                model = auto_arima(df_close, trace=True, error_action='ignore', suppress_warnings=True)
                model.fit(df_close)
                forecast = model.predict(n_periods=3)
                trend = []
                for f in range(len(forecast.tolist())):
                    if f == 0:
                        if forecast.tolist()[0] >= load_data(Ticker)[-1:].Close.to_list()[0]:
                            trend.append("Bull/Up")
                        else:
                            trend.append("Bear/Down")
                    else:
                        if forecast.tolist()[f] >= forecast.tolist()[f - 1]:
                            trend.append("Bull/Up")
                        else:
                            trend.append("Bear/Down")
                data = {'Date': early, 'Prediction': [round(f, 2) for f in forecast.tolist()], 'Trend': trend}
                forecast = pd.DataFrame(data=data)
                return forecast

            if today not in predictions:
                predictions[today] = {}
                if value not in predictions[today]:
                    predictions[today][value] = predict(value)
                    columns = [{"name": i, "id": i} for i in predictions[today][value].columns]
                    print(columns)
                    t_data = predictions[today][value].to_dict("records")
                    return columns, t_data
                else:
                    columns = [{"name": i, "id": i} for i in predictions[today][value].columns]
                    print(columns)
                    t_data = predictions[today][value].to_dict("records")
                    return columns, t_data
            else:
                if value not in predictions[today]:
                    predictions[today][value] = predict(value)
                    columns = [{"name": i, "id": i} for i in predictions[today][value].columns]
                    print(columns)
                    t_data = predictions[today][value].to_dict("records")
                    return columns, t_data
                else:
                    columns = [{"name": i, "id": i} for i in predictions[today][value].columns]
                    print(columns)
                    t_data = predictions[today][value].to_dict("records")
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
            ans = gen(value)
            ans["Info"].insert(0, value)
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
            return summary(su(value))

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

    @app.callback(
        Output("vol", "figure"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def current(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=load_data(value)[-5:].Volume.to_list()[-1],
                delta={'reference': load_data(value)[-5:].Volume.to_list()[-2], "valueformat": ".0f"},
                title={'text': "Volume"},
                domain={'y': [0, 1], 'x': [0.25, 0.75]}
            ))

            fig.add_trace(go.Scatter(x=list(load_data(value).index),
                                     y=load_data(value).Volume.to_list()))
            fig.update_layout(margin=dict(
                l=0, r=0, t=0, b=0)
            )
            return fig

    @app.callback(
        Output("col", "figure"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def current(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=load_data(value)[-5:].Close.to_list()[-1],
                delta={'reference': load_data(value)[-5:].Close.to_list()[-2], "valueformat": ".0f"},
                title={'text': "Close"},
                domain={'y': [0, 1], 'x': [0.25, 0.75]}
            ))

            fig.add_trace(go.Scatter(y=load_data(value)[-6:].Close.to_list()))
            fig.update_layout(xaxis={'range': [1, 5]},
                              margin=dict(
                                  l=0, r=0, t=20, b=0
                              ),
                              height=250)
            return fig

    @app.callback(
        Output("open", "figure"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def current(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=load_data(value)[-5:].Open.to_list()[-1],
                delta={'reference': load_data(value)[-5:].Open.to_list()[-2], "valueformat": ".0f"},
                title={'text': "Open"},
                domain={'y': [0, 1], 'x': [0.25, 0.75]}
            ))

            fig.add_trace(go.Scatter(y=load_data(value)[-6:].Open.to_list()))
            fig.update_layout(xaxis={'range': [1, 5]},
                              margin=dict(
                                  l=0, r=0, t=20, b=0
                              ),
                              height=250)
            return fig

    @app.callback(
        Output("high", "figure"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def current(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=load_data(value)[-5:].High.to_list()[-1],
                delta={'reference': load_data(value)[-5:].High.to_list()[-2], "valueformat": ".0f"},
                title={'text': "High"},
                domain={'y': [0, 1], 'x': [0.25, 0.75]}
            ))

            fig.add_trace(go.Scatter(y=load_data(value)[-6:].High.to_list()))
            fig.update_layout(xaxis={'range': [1, 5]},
                              margin=dict(
                                  l=0, r=0, t=20, b=0
                              ),
                              height=250)
            return fig

    @app.callback(
        Output("low", "figure"),
        Input("Search", "n_clicks"),
        State("Stock", "value")
    )
    def current(n_clicks, value):
        if value is None:
            raise dash.exceptions.PreventUpdate
        else:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=load_data(value)[-5:].Low.to_list()[-1],
                delta={'reference': load_data(value)[-5:].Low.to_list()[-2], "valueformat": ".0f"},
                title={'text': "Low"},
                domain={'y': [0, 1], 'x': [0.25, 0.75]}
            ))

            fig.add_trace(go.Scatter(y=load_data(value)[-6:].Low.to_list()))
            fig.update_layout(xaxis={'range': [1, 5]},
                              margin=dict(
                                  l=0, r=0, t=20, b=0
                              ),
                              height=250)
            return fig

    return app.server
