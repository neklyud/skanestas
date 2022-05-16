"""Routers for tickers api."""


import http
from datetime import datetime
from typing import List

from app.options import get_influx
from fastapi import APIRouter, Depends, HTTPException
from influxdb_client.client.influxdb_client_async import QueryApiAsync
from pydantic import BaseModel


class Point(BaseModel):
    """Model of point in influxdb."""

    measure: int
    time: datetime


router = APIRouter()


@router.get('/history/{ticker}')
async def load_history(
        ticker: str,
        period: str,
        influx_api: QueryApiAsync = Depends(get_influx),
) -> List[Point]:
    """
    Get prices for some ticker.

    Args:
        ticker (str): ticker name.
        period (str): query window.
        influx_api (QueryApiAsync): instance of influx api.

    Returns:
        List[Point]: list with prices.
    """
    query_string = f' from(bucket:"tickers")\
    |> range(start: {period})\
    |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
    |> filter(fn: (r) => r["_field"] == "price")'  # noqa: N400
    points = []
    tables = await influx_api.query(query_string)
    for table in tables:
        for row in table.records:
            points.append(Point(
                **{'measure': row.get_value(), 'time': row.get_time()},
            ))
    return points


@router.get('/price/{ticker}')
async def get_price(
        ticker: str,
        period: str,
        influx_api: QueryApiAsync = Depends(get_influx),
) -> Point:
    """
    Get lasr price for some ticker.

    Args:
        ticker (str): ticker name.
        period (str): query window.
        influx_api (QueryApiAsync): instance of influx api.

    Returns:
        Point: object that contains ticker price and time of deal.

    Raises:
        HTTPException: if prices not found.
    """
    query_string = f' from(bucket:"tickers")\
    |> range(start: {period})\
    |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
    |> filter(fn: (r) => r["_field"] == "price")\
    |> last()'  # noqa: N400
    prices = await influx_api.query(query_string)
    if not prices or not prices[0].records[0]:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST, detail='No data.',
        )
    return Point(
        **{  # noqa: WPS517
            'time': prices[0].records[0].get_time(),
            'measure': prices[0].records[0].get_value(),
        },
    )


@router.get('/measurments')
async def get_measurments(
        bucket: str,
        influx_api: QueryApiAsync = Depends(get_influx),  # noqa: WPS404, B008
) -> List[str]:
    """
    Get measurments router.

    Gets measurments names from influx.

    Args:
        bucket (str): name of bucket.
        influx_api (QueryApiAsync): instance of influx api.

    Returns:
        List[str]: returns measurments names.
    """
    query_string = f"""
    import \"influxdata/influxdb/schema\"

    schema.measurements(bucket: \"{bucket}\")
    """
    tables = await influx_api.query(query_string)
    return [row.values['_value'] for table in tables for row in table]
