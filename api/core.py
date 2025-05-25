from fastapi import FastAPI
from api.collector import api as collector
from api.pdf_extractor import api as pdf_extractor

app = FastAPI()

app.include_router(collector.router)
app.include_router(pdf_extractor.router)
