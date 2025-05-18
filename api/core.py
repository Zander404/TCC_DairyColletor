from fastapi import FastAPI
from api.collector import core as collector

app = FastAPI()

app.include_router(collector.router)
