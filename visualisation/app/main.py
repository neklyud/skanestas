import json

import influxdb_client
import plotly
from dash import Dash, html, dcc, Input, Output


from loader import InfluxLoader

app = Dash(__name__)


def get_options():
    with open('tickers.json', 'r') as json_file:
        json_data = json.loads(json_file.read())
        return json_data['data']


app.layout = html.Div(
    children=[
        html.H1(children='Skanestas test task'),
        html.Div(children='Ticker prices.'),
        html.Div(id='live-update-text'),
        dcc.Dropdown(id='ticker', options=get_options(), value=get_options()[0]),
        dcc.Graph(id='tickers-graphic'),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
    ]
)


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    import random

    lon, lat, alt = random.randint(0, 10), random.randint(0, 4), random.randint(0, 10)
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Longitude: {0:.2f}'.format(lon), style=style),
        html.Span('Latitude: {0:.2f}'.format(lat), style=style),
        html.Span('Altitude: {0:0.2f}'.format(alt), style=style)
    ]


@app.callback(
    Output('tickers-graphic', 'figure'),
    Input('ticker', 'value'),
    Input('interval-component', 'n_intervals'),
    log=True
)
def load_graphic(ticker: str, _: int):
    influx_client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token='token-test', org='skanestas')
    data = InfluxLoader(influx_client).get_history(ticker)
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig.append_trace({
        'x': data.index,
        'y': data['measurement']
    }, 1, 1)
    influx_client.close()
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
