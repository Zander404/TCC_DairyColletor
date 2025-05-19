from fastapi import APIRouter
from api.collector import core

router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}


@router.post("/colect_data")
def start_collect_data():
