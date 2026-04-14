from api.v1.collector.controller import router as collector_routers
from fastapi import FastAPI

app = FastAPI()

app.include_router(collector_routers)
# app.include_router(pdf_extractor.router)
