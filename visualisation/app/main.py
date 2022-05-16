"""Visualisation module."""

import asyncio
import logging

import plotly
from app.conf import config
from app.request import RequestHelper
from dash import Dash, Input, Output, dcc, html

app = Dash(__name__)
server = app.server


def get_options() -> list:
    """
    Return measures.

    Returns:
        list: list of tickers names.
    """
    measurements = asyncio.run(
        RequestHelper.get(
            url=f'{config.url}/api/measurments',
            req_params={'bucket': 'tickers'},
        ),
    )
    return [i_data for i_data in measurements if i_data.startswith('tickers')]


app.layout = html.Div(
    children=[
        html.H1(children='Skanestas test task'),
        html.Div(children='Ticker prices.'),
        dcc.Dropdown(
            id='ticker', options=get_options(), value=get_options()[0],
        ),
        dcc.Graph(id='tickers-graphic'),
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    ],
)


@app.callback(
    Output('tickers-graphic', 'figure'),
    Input('ticker', 'value'),
    Input('interval-component', 'n_intervals'),
    log=True,
)
def load_graphic(ticker: str, _: int):
    """
    Load and update graph function.

    UPD: хотел сделать подгрузку только последнего элемента
    в процессе отображения графика по тикеру, но не успел.

    Args:
        ticker (str): name of ticker.
        _ (int): pass.
    Returns:
        figure
    """  # noqa: DAR102, DAR003, DAR201
    period_param = {'period': config.history_load_period}
    tickers_history = asyncio.run(
        RequestHelper.get(
            url=f'{config.url}/api/history/{ticker}', req_params=period_param,
        ),
    )
    logging.info(tickers_history)
    spacing_val = 0.2
    fig = plotly.tools.make_subplots(
        rows=2, cols=1, vertical_spacing=spacing_val,
    )
    fig.append_trace(
        {
            'x': [i_data['time'] for i_data in tickers_history],
            'y': [i_data['measure'] for i_data in tickers_history],
            'name': 'Ticker prices.',
        },
        1,
        1,
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
