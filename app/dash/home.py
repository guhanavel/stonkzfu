from datetime import datetime

import dash_bootstrap_components
import google.protobuf.internal.wire_format
from dash import callback_context

from app.dash.function import *
import warnings

warnings.filterwarnings('ignore')

NASQ = read_csv(r"app/static/AAll.csv")
opt = lookup(NASQ)


def dash_pp(server):
    dap = dash.Dash(server=server, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP],
                    title="Stonkzfu",
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1'}])

    search_bar = dbc.Row(
        [
            dbc.Col(dcc.Dropdown(id='Stock', options=opt),
                    style={'height': '30px', 'width': '100px', "padding-left": "10px", "border-radius": "25px"}),
            dbc.Col(
                html.A(
                    html.Img(src="../static/search.png", height="20vh"), id="Search", href="/das/?val=AAPL"
                ),
                width="auto",
                style={"padding": "0%"}
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    )

    head = [html.Div(id="test"),
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
                    html.A("Dashboard", href='/das/?val=AAPL'), html.A("Calendar", href='/cal')
                ])
            ])), html.Li(html.A(html.Img(src="../static/logo.png", height="50vh"), href="/"))])),
            html.Marquee(id="price"),
            dbc.Row([dbc.Col(html.Div([search_bar], style={"overflow": "visible"}), xs=12, sm=12, md=12, lg=4, xl=4),
                     dbc.Col(html.Div(id="time"), xs=12, sm=12, md=12, lg={"size": 4, "offset": 4},
                             xl={"size": 4, "offset": 4})]),
            dbc.Row(dbc.Col(html.Div([
                dbc.ButtonGroup([
                    dbc.Button("Gainers", id="gain", color="light", n_clicks=0),
                    dbc.Button('Losers', id='lose', color="light", n_clicks=0),
                    dbc.Button('Active', id="active", color="light", n_clicks=0),
                ],
                    size='sm')]), style={'whiteSpace': 'nowrap'})),
            dbc.Row(html.Div([dash_table.DataTable(
                id='perform',
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ["Symbol", "Name", "Price", "Change", "% Change"]
                ],
                style_data={
                    'color': 'black',
                    'backgroundColor': 'white',
                    'whiteSpace':'left',
                    'minWidth':'80px', 'width':'80px','maxWidth':'80px'
                },
                style_cell={
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                }

            ), ]))

            ]
    CONTENT_STYLE = {
        "background-color": "#f8f9fa",
    }
    content = html.Div(head, id="page-content", style=CONTENT_STYLE)

    dap.layout = html.Div([dcc.Location(id="url", refresh=False),
                           content], style={"overflow": "visible"})

    @dap.callback(Output('Search', 'href'), Input("Stock", "value"))
    def out(value):
        return '/das/?val=' + str(value)

    @dap.callback(Output("time", "children"), Input('interval-component', 'n_intervals'))
    def tim(n):
        return serve_layout()

    @dap.callback(Output("price", "children"), Input('tilt', 'n_intervals'))
    def price(n):
        return prices(["AAPL", "MSFT", "AMZN", "GOOGL", "FB", "NVDA", "UNH"])

    @dap.callback(
        [Output("perform", "columns"), Output("perform", "data")],
        Input("active", "n_clicks"), Input("gain", "n_clicks"),
        Input("lose", "n_clicks")
    )
    def top(a, g, l):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if "active" in changed_id:
            data = active()
        elif "gain" in changed_id:
            data = gain()
        elif "lose" in changed_id:
            data = lose()
        else:
            data = gain()
        columns = [{"name": i, "id": i} for i in data.columns]
        t_data = data.to_dict("records")
        return columns, t_data

    return dap.server
