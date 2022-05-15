import asyncio

from fastapi import FastAPI
from app.api import router
from app.options import read_tickers
from app.async_generator import GeneratorManager

app = FastAPI()
app.include_router(router, prefix="/api", tags=["api"])


@app.on_event("startup")
async def startup():
    tickers = read_tickers("app/tickers.json")
    # asyncio.create_task(GeneratorManager.run(tickers['data']))
