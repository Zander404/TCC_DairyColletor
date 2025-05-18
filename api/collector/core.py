from fastapi import APIRouter


router = APIRouter(prefix="/pubmed", tags=["PubMed"])


@router.get("/")
def index():
    return {"Data": "Hello Word"}
