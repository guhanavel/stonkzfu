from datetime import datetime

import dash_bootstrap_components
import google.protobuf.internal.wire_format

from app.dash.function import *
import warnings

warnings.filterwarnings('ignore')

NASQ = read_csv(r"app/static/AAll.csv")
opt = lookup(NASQ)


def dash_app(server):
    app = dash.Dash(server=server, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP],
                    title="Stonkzfu",
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1, maximum-scale=1.2, minimum-scale=0.5'}])

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.

    CONTENT_STYLE = {
        "transition": "margin-left .5s",
        "background-color": "#f8f9fa",
    }

    search_bar = dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='Stock', options=opt),
                    style={'height': '30px', 'width': '100px', "padding-left": "10px"}),
            dbc.Col(
                dbc.Button(
                    html.Img(src="../static/search.png", height="20vh"), id="Search", n_clicks=0, color="light",
                ),
                width="auto",
                style={"padding": "0%"}
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    cdivs = [html.Div(id="test"),
             dcc.Interval(
                 id='interval-component',
                 interval=1 * 10000,  # in milliseconds
                 n_intervals=0
             ),
             dcc.Interval(
                 id='inter',
                 interval=1 * 500,  # in milliseconds
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
             dbc.Row(search_bar),
             dbc.Row(html.Div(id="Test")),
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

    content = html.Div(cdivs, id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url", refresh=False),
                           content], )

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

    @app.callback(
        Output('graph_close', 'figure'),
        Input('url', 'search'), Input('interval-component', 'n_intervals'))
    def lota(search, n):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            dat = load_data(search[5:])
            MA_200 = dat.rolling(window=200).mean()
            MA_50 = dat.rolling(window=50).mean()
            fig = make_subplots(rows=4, cols=2, specs=[[{"type": "indicator", "rowspan": 1, "colspan":1},{"type": "indicator", "rowspan": 1, "colspan":1}],
                                                       [{"type": "scatter", "rowspan": 2, "colspan":2},None],
                                                       [None,None],
                                                       [{"type": "bar", "rowspan": 1,"colspan":2},None]])
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=live_prices(search[5:])[1],
                    number={'valueformat': 'f', 'suffix':"USD","font":{"size":20}},
                    title={"text":"Status:"+str(live_prices(search[5:])[0]), "font":{"size":30},"align":"left"},
                    delta={'reference': live_prices(search[5:])[2], 'relative': True, 'position': "bottom"},
                    align="left",

                ),
                row=1, col=1
            ),
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=live_prices(search[5:])[-1],
                    number={'valueformat': 'f', 'suffix': "USD", "font": {"size": 20}},
                    title={"text": str(live_prices(search[5:])[0]) + ":", "font": {"size": 30}, "align": "left"},
                    delta={'reference': live_prices(search[5:])[-2], 'relative': True, 'position': "bottom"},
                    align="left",
                    visible=False if live_prices(search[5:])[0] == "Open" else True,
                    uid="pos"

                ),
                row=1, col=2
            )
            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(dat.Close),
                                     visible=True,
                                     name="Close",
                                     showlegend=True), row=2, col=1)

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_200.Close),
                                     visible=True,
                                     name="MA_200",
                                     showlegend=True), row=2, col=1)

            fig.add_trace(go.Scatter(x=list(dat.index),
                                     y=list(MA_50.Close),
                                     visible=True,
                                     name="MA_50",
                                     showlegend=True,
                                     ), row=2, col=1)
            fig.add_trace(go.Bar(x=list(dat.index),
                                 y=list(dat.Volume),
                                 name="Volume", ),
                          row=4, col=1)

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
        Input('url', 'search')
    )
    def date(search):
        if search[5:] is None:
            raise dash.exceptions.PreventUpdate
        else:
            ans = news_api(search[5:])
            fin = pd.DataFrame(data=ans)
            return dbc.Table.from_dataframe(fin, striped=True, bordered=True, hover=True, loading_state=True)

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

        return sidebar_style, content_style, cur_nclick

    @app.callback(Output('test', 'children'),
                  Input('inter', 'n_intervals'))
    def inter(n):
        return serve_layout()
    return app.server
