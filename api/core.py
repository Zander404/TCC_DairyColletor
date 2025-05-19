from fastapi import FastAPI
from api.collector import api as collector

app = FastAPI()

app.include_router(collector.router)
