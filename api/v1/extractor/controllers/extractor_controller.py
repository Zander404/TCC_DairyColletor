import io
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.v1.extractor.services.extractor_services import ExtractorServices
import pandas as pd

router = APIRouter(prefix="/extractor_pdf")


def get_services():
    return ExtractorServices()


SERVICES_DEP = Annotated[ExtractorServices, Depends(get_services)]


@router.post("")
async def start_extract_book(services: SERVICES_DEP):
    csv_extract: pd.DataFrame = services.extract_pdf()

    output_stream = io.StringIO()
    csv_extract.to_csv(output_stream, index=False)

    output_stream.seek(0)
    return StreamingResponse(
        output_stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=qa_from_500perguntasgadoleiteiro.csv"
        },
    )
