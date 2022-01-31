from datetime import datetime

import dash_bootstrap_components
import google.protobuf.internal.wire_format
from dash import callback_context

from app.dash.function import *
import warnings

warnings.filterwarnings('ignore')

NASQ = read_csv(r"app/static/AAll.csv")
opt = lookup(NASQ)


def dash_app(server):
    app = dash.Dash(server=server, url_base_pathname='/das/', external_stylesheets=[dbc.themes.BOOTSTRAP],
                    title="Stonkzfu",
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1'}])

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.

    CONTENT_STYLE = {
        "background-color": "#f8f9fa",
    }

    search_bar = dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='Stock', options=opt),
                    style={'height': '30px', 'width': '100px', "padding-left": "10px","border-radius":"25px"}),
            dbc.Col(
                dbc.Button(
                    html.Img(src="../static/search.png", height="20vh"), id="Search", n_clicks=0, color="light",
                ),
                width="auto",
                style={"padding": "0%"}
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    )

    cdivs = [html.Div(id="test"),
             dcc.Interval(
                 id='interval-component',
                 interval=1 * 1000,  # in milliseconds
                 n_intervals=0
             ),
             dcc.Interval(
                 id='tilt',
                 interval=10000,  # in milliseconds
                 n_intervals=0
             ),
             dcc.Interval(
                 id='milian',
                 interval=1 * 60000,  # in milliseconds
                 n_intervals=0
             ),
             html.Div(html.Ul(children=[html.Li(html.Div(className="dropdown", children=[
                 html.Button(className="dropbtn", children=[
                     html.Img(src="../static/options.png", height="30vh")
                 ]),
                 html.Div(className="dropdown-content", children=[
                     html.A("Home", href='/'), html.A("Calendar", href='/cal')
                 ])
             ])), html.Li(html.A(html.Img(src="../static/logo.png", height="50vh"), href="/"))])),
             html.Marquee(id="price"),
             dbc.Row([dbc.Col(html.Div([search_bar]),xs=12, sm=12, md=12, lg=4, xl=4),dbc.Col(html.Div(id="time"),xs=12, sm=12, md=12, lg={"size":4,"offset":4}, xl={"size":4,"offset":4})]),
             dbc.Row(
                 [dbc.Col(html.Div([
                     dcc.Graph(

                         id="data",
                         config={
                             'displayModeBar': False
                         },
                     ),
                     html.H4("Charts:"),
                     dbc.Row(dbc.Col(html.Div([
                         dbc.ButtonGroup([
                             dbc.Button("1D", id="1d", color="light", n_clicks=0),
                             dbc.Button('5D', id='5d', color="light", n_clicks=0),
                             dbc.Button('1M', id="1m", color="light", n_clicks=0),
                             dbc.Button('6M', id='6m', color="light", n_clicks=0),
                             dbc.Button('YTD', id='ytd', color="light", n_clicks=0),
                             dbc.Button("1Y", id='1y', color="light", n_clicks=0),
                             dbc.Button("5Y", id='5y', color="light", n_clicks=0),
                             dbc.Button("MAX", id='max', color="light", n_clicks=0)
                         ],
                             size='sm')]), style={'whiteSpace': 'nowrap'})),
                     dcc.Graph(
                         id="graph_close",
                         config={
                             'displayModeBar': False
                         },
                         style={'width': '98h', "-webkit-overflow-scrolling": "touch"},
                     ),
                     dcc.Graph(
                         id="vol",
                         config={
                             'displayModeBar': False
                         },
                         style={'width': '98h', "-webkit-overflow-scrolling": "touch"},
                     )
                 ]), xs=12, sm=12, md=12, lg=8, xl=8),

                     dbc.Col(
                         html.Div([
                             html.H4('General Information:'),
                             html.Div(id='gen', style={"align": "left"}),
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
                         ]),
                         xs=12, sm=12, md=12, lg=4, xl=4),
                 ], justify='left', align="left"),
             dbc.Row(
                 [

                     dbc.Col(html.Div([
                         html.Div([
                             html.H4("News:"),
                             html.Div([
                                 dcc.DatePickerRange(
                                     id='my-date-picker-range',
                                     min_date_allowed=dt(1990, 1, 1),
                                     max_date_allowed=dt.today(),
                                     initial_visible_month=dt.today(),
                                     end_date=dt.today(),
                                     start_date=dt.today()-e
                                 ),
                             ]),
                             html.Div(id='news',className="scrollmenu"),
                         ]
                         ),
                     ]), width={"size": 6}, xs=12, sm=12, md=12, lg=12, xl=12),
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

                     ]), style={'padding-top': '0.5rem'}, width={"size": 12}, xs=12, sm=12, md=12, lg=3, xl=3),
                     dbc.Col(html.Div([
                         html.H4('Recommendation:'),
                         html.Div(id="recc")]), width={"size": 12}, xs=12, sm=12, md=12, lg=3, xl=3),
                     dbc.Col(html.Div([
                         html.H4('Social Media Trends:'),
                         dcc.Graph(
                             id="social",
                             config={
                                 'displayModeBar': False
                             },
                             style={'width': '98h'},
                         ),
                     ]), xs=12, sm=12, md=12, lg=6, xl=6)

                 ]),
             dbc.Row(
                 [
                     dbc.Col(
                         html.Div([
                             html.H4('About Company'),
                             html.P(id="infom", style={"font-size": "small"})
                         ])),

                 ], ),
             ]

    content = html.Div(cdivs, id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url", refresh=False),
                           content], style={"overflow": "hidden"})

    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to tell see page they are on
    @app.callback(Output('url', 'search'), Input("Search", "n_clicks"),
                  State("Stock", "value"))
    def out(n_clicks, value):
        if isinstance(value, str):
            return '?val=' + value

    @app.callback(Output("Stock", "value"), Input('url', 'search'))
    def input(search):
        return search[5:]

    @app.callback(Output("time", "children"), Input('interval-component', 'n_intervals'))
    def tim(n):
        return serve_layout()

    @app.callback(Output('milian', "interval"), Input('url', 'search'))
    def check(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            if stock_info.get_market_status() == "OPEN":
                return 60000
            elif stock_info.get_market_status() == "OPEN":
                return 60000
            else:
                return 36000000

    @app.callback(Output('data', 'figure'),
                  Input('url', 'search'), Input('tilt', 'n_intervals'))
    def lota(search, n):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            status = stock_info.get_market_status()
            fig = make_subplots(rows=2, cols=1, specs=[[{"type": "indicator", "rowspan": 1, "colspan": 1}],
                                                       [{"type": "indicator", "rowspan": 1, "colspan": 1}],
                                                       ],
                                vertical_spacing=0)
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=live_prices(search[5:])[2],
                    number={'valueformat': 'f', 'suffix': "USD", "font": {"size": 35}},
                    delta={'reference': live_prices(search[5:])[1], 'relative': True, 'position': "bottom"},
                    align="left",

                ),
                row=1, col=1
            ),
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=live_prices(search[5:])[-1],
                number={'valueformat': 'f', 'suffix': "USD", "font": {"size": 20},
                        'prefix': str(live_prices(search[5:])[0]) + ":"},
                delta={'reference': live_prices(search[5:])[2] if status == "CLOSED" else live_prices(search[5:])[1],
                       'relative': True, 'position': "bottom"},
                align="left",
                visible=True if live_prices(search[5:])[0] != "Open" else False,

            ),

                row=2, col=1

            )
            fig.update_layout(
                autosize=False,
                height=100,
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    x=0,
                    y=0.5,
                    traceorder="normal",

                ),
            ),

            return fig

    @app.callback(
        Output('graph_close', 'figure'),
        Input('url', 'search'), Input('milian', 'n_intervals'), Input("1d", "n_clicks"), Input("5d", "n_clicks"),
        Input("1m", "n_clicks"), Input("6m", "n_clicks"), Input("ytd", "n_clicks"), Input("1y", "n_clicks"),
        Input("5y", "n_clicks"), Input("max", "n_clicks"), )
    def lota(search, n, d1, d5, m1, m6, yd, y1, y5, ma):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            if '5d' in changed_id:
                dat = load_data(search[5:], '5d', '15m', True)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif '1d' in changed_id:
                dat = load_data(search[5:], '1d', '5m', False)
                op = min(dat.index)
                cl = min(dat.index) + hour
                vis = True
            elif '1m' in changed_id:
                dat = load_data(search[5:], '1mo', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif '6m' in changed_id:
                dat = load_data(search[5:], '6mo', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif 'ytd' in changed_id:
                dat = load_data(search[5:], 'ytd', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif '1y' in changed_id:
                dat = load_data(search[5:], '1y', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif '5y' in changed_id:
                dat = load_data(search[5:], '5y', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            elif 'max' in changed_id:
                dat = load_data(search[5:], 'max', '5d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
                vis = False
            else:
                dat = load_data(search[5:], '1d', '2m', False)
                op = min(dat.index)
                cl = min(dat.index) + hour
                vis = True
            status = stock_info.get_market_status()
            dan = yf.download(search[5:], period="5d")
            if status == "REGULAR":
                yes = float(dan[-2:-1].Close)  # previous
            elif status == "CLOSED":
                yes = float(dan[-2:-1].Close)  # previous
            else:
                yes = float(dan[-1:].Close)  # previous
            lower = min(yes, min(list(dat.Close))) * 0.98
            upper = max(list(dat.Close)) * 1.02

            def what():
                if live_prices(search[5:])[2] > dat.Close.iloc[0]:
                    return 'green'
                elif live_prices(search[5:])[2] < dat.Close.iloc[0]:
                    return 'red'
                else:
                    return 'grey'

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(dat.Close),
                                     visible=True,
                                     name="Close",
                                     showlegend=True,
                                     line=dict(color=what(), width=1),
                                     stackgroup='one'))

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=[yes, ] * 420,
                                     visible=vis,
                                     name="Previous-Close",
                                     line=dict(color='black', width=4, dash='dot')))

            fig.update_layout(
                autosize=False,
                hovermode="x unified",
                yaxis=dict(range=[lower, upper], fixedrange=True),
                xaxis=dict(
                    fixedrange=True,
                    range=[op, cl],
                    type='date'),
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    x=0,
                    y=1,
                    traceorder="normal",

                ),
            )
            return fig

    @app.callback(
        Output('vol', 'figure'),
        Input('url', 'search'), Input('milian', 'n_intervals'), Input("1d", "n_clicks"), Input("5d", "n_clicks"),
        Input("1m", "n_clicks"), Input("6m", "n_clicks"), Input("ytd", "n_clicks"), Input("1y", "n_clicks"),
        Input("5y", "n_clicks"), Input("max", "n_clicks"), )
    def lota(search, n, d1, d5, m1, m6, yd, y1, y5, ma):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            if '5d' in changed_id:
                dat = load_data(search[5:], '5d', '15m', True)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            elif '1d' in changed_id:
                dat = load_data(search[5:], '1d', '5m', False)
                op = min(dat.index)
                cl = min(dat.index) + hour
            elif '1m' in changed_id:
                dat = load_data(search[5:], '1mo', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            elif '6m' in changed_id:
                dat = load_data(search[5:], '6mo', '1d', False)
                op = min(dat.index).date()

                cl = max(dat.index).date()
            elif 'ytd' in changed_id:
                dat = load_data(search[5:], 'ytd', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            elif '1y' in changed_id:
                dat = load_data(search[5:], '1y', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            elif '5y' in changed_id:
                dat = load_data(search[5:], '5y', '1d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            elif 'max' in changed_id:
                dat = load_data(search[5:], 'max', '5d', False)
                op = min(dat.index).date()
                cl = max(dat.index).date()
            else:
                dat = load_data(search[5:], '1d', '2m', False)
                op = min(dat.index)
                cl = min(dat.index) + hour
            fig = go.Figure(data=[go.Bar(x=list(dat.index),
                                         y=list(dat.Volume),
                                         name="Volume", )])

            fig.update_layout(
                autosize=False,
                height=80,
                yaxis=dict(fixedrange=True, ),
                xaxis=dict(
                    fixedrange=True,
                    range=[op, cl],
                    type='date'),
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    x=0,
                    y=1,
                    traceorder="normal",

                ),
            )
            return fig

    @app.callback(
        [Output("table", "columns"), Output("table", "data")],
        Input('url', 'search')
    )
    def day(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            data = predict(search[5:])
            columns = [{"name": i, "id": i} for i in data.columns]
            print(columns)
            t_data = data.to_dict("records")
            return columns, t_data

    @app.callback(
        Output("gen", "children"),
        Input('url', 'search')
    )
    def date(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            ans = info(search[5:])
            fin = pd.DataFrame(data=ans)
            return dbc.Table.from_dataframe(fin, striped=True, bordered=True, hover=True, loading_state=True)

    @app.callback(
        Output("news", "children"),
        Input('url', 'search'), Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    )
    def date(search,start_date,end_date):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            if start_date is not None:
                start_date_object = dt.fromisoformat(start_date)
                start = start_date_object.strftime('%m/%d/%Y')
            if end_date is not None:
                end_date_object = dt.fromisoformat(end_date)
                end = end_date_object.strftime('%m/%d/%Y')
            ans = news_api(search[5:],start,end)
            return ans

    @app.callback(
        Output("infom", "children"),
        Input('url', 'search')
    )
    def get(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            return summary(search[5:])

    @app.callback(
        [Output("earn", "columns"), Output("earn", "data")],
        Input("mode", "value"),
        Input('url', 'search')
    )
    def ear(value, search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            fin = earnings(search[5:], value)
            fin.rename(columns={'date': 'Date', 'actual': 'Actual', 'estimate': 'Estimate', 'revenue': 'Revenue',
                                'earnings': 'Earnings'}, inplace=True)
            columns = [{"name": i, "id": i} for i in fin.columns]
            t_data = fin.to_dict("records")
            return columns, t_data

    @app.callback(
        Output("recc", "children"),
        Input('url', 'search')
    )
    def recc(search):
        indi = daq.Gauge(
            color={
                "ranges": {
                    "red": [0, 2],
                    "pink": [2, 4],
                    "#ADD8E6": [4, 6],
                    "#4169E1": [6, 8],
                    "blue": [8, 10],
                },
            },
            scale={
                "custom": {
                    1: {"label": "Strong Sell"},
                    3: {"label": "Sell"},
                    5: {"label": "Neutral"},
                    7: {"label": "Buy"},
                    9: {"label": "Strong Buy"},
                }
            },
            value=recom(search[5:])[0],
            max=10,
            min=0,
            label="As off:" + " " + str(recom(search[5:])[1]),
            style={"font-size": "20px"}
        )
        return indi

    @app.callback(
        Output('social', 'figure'),
        Input('url', 'search'), )
    def social(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            indices = sm(search[5:]).index
            reddit = sm(search[5:])["red_add"]
            twitter = sm(search[5:])["twi_add"]
            overall = sm(search[5:])["o_sum"]
            red_m = sm(search[5:])["red_mention"]
            twi_m = sm(search[5:])["twi_mention"]
            mention = sm(search[5:])["mention"]
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Sentiment Score", "Mentions"))
            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(reddit),
                                     visible=True,
                                     name="Reddit",
                                     showlegend=True,
                                     line=dict(color='red', width=1)), row=1, col=1)

            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(twitter),
                                     visible=True,
                                     name="Twitter",
                                     line=dict(color='blue', width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(overall),
                                     visible=True,
                                     name="Overall",
                                     line=dict(color='black', width=1)), row=1, col=1)
            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(red_m),
                                     visible=True,
                                     name="Reddit",
                                     showlegend=False,
                                     line=dict(color='red', width=1)), row=1, col=2)
            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(twi_m),
                                     visible=True,
                                     name="Twitter",
                                     showlegend=False,
                                     line=dict(color='blue', width=1)), row=1, col=2)
            fig.add_trace(go.Scatter(x=list(indices),
                                     y=list(mention),
                                     visible=True,
                                     name="Overall",
                                     showlegend=False,
                                     line=dict(color='black', width=1)), row=1, col=2)
            fig.update_layout(
                autosize=False,
                hovermode="x unified",
                height=250,
                yaxis=dict(fixedrange=True, ),
                xaxis=dict(
                    fixedrange=True,
                    type='date'),
                margin=dict(
                    l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    x=0,
                    y=1,
                    traceorder="normal",

                ),
            ),
        return fig

    @app.callback(Output("price","children"),Input('tilt', 'n_intervals'))
    def sy(n):
        return prices(["AAPL","MSFT","AMZN","GOOGl","FB","NVDA","UNH"])
    return app.server
