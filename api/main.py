from api.v1.collector.controller import router as collector_routers
from api.v1.extractor.controllers.download_controller import router as download_routers
from api.v1.extractor.controllers.extractor_controller import (
    router as extractor_routers,
)
from api.v1.modelo.controller import routers as models_routers

from fastapi import FastAPI

app = FastAPI()

app.include_router(collector_routers)
app.include_router(extractor_routers, tags=["EXTRACTOR - PDF"])
app.include_router(download_routers, tags=["EXTRACTOR - DOWNLOAD"])
app.include_router(models_routers, tags=["MODELOS"])
