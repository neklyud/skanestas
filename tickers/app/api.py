from fastapi import APIRouter, Depends, HTTPException
from app.options import get_influx
from influxdb_client.client.influxdb_client_async import QueryApiAsync
from pydantic import BaseModel
from datetime import datetime
import http


class Point(BaseModel):
    measure: int
    time: datetime


class PointList(BaseModel):
    points: list[Point]


router = APIRouter()


@router.get("/history/{ticker}")
async def load_history(ticker: str, period: str, influx_api: QueryApiAsync = Depends(get_influx)) -> list[Point]:
    query_string = f' from(bucket:"tickers")\
    |> range(start: {period})\
    |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
    |> filter(fn: (r) => r["_field"] == "price")'
    points = []
    tables = await influx_api.query(query_string)
    for table in tables:
        for row in table.records:
            point = Point(**{"measure": row.get_value(), "time": row.get_time()})
            points.append(point)
    return points


@router.get("/price/{ticker}")
async def get_price(ticker: str, period: str, influx_api: QueryApiAsync = Depends(get_influx)) -> Point:
    query_string = f' from(bucket:"tickers")\
    |> range(start: {period})\
    |> filter(fn: (r) => r["_measurement"] == "{ticker}")\
    |> filter(fn: (r) => r["_field"] == "price")\
    |> last()'
    result = await influx_api.query(query_string)
    if not result or not result[0].records[0]:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST, detail="No data.")
    return Point(**{"time": result[0].records[0].get_time(), "measure": result[0].records[0].get_value()})


@router.get("/measurments")
async def get_measurments(bucket: str, influx_api: QueryApiAsync = Depends(get_influx)) -> list[str]:
    query_string = f"""
    import \"influxdata/influxdb/schema\"

    schema.measurements(bucket: \"{bucket}\")
    """
    tables = await influx_api.query(query_string)
    measurements = [row.values["_value"] for table in tables for row in table]
    return measurements
