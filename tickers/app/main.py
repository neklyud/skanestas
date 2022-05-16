"""Main function."""

import asyncio

from app.api import router
from app.async_generator import GeneratorManager
from app.options import read_tickers
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix='/api', tags=['api'])


@app.on_event('startup')
async def startup():
    """Startup function."""
    tickers = read_tickers('app/tickers.json')
    asyncio.create_task(GeneratorManager.run(tickers['data']))
