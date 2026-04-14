import io
import pandas as pd

from fastapi import File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from api.v1.collector.clients.pubmed_client import PubMedClient
from api.v1.collector.utils.constants import PATH_COLLECTOR


async def start_collect_article_id_pub_med(
    start: int = 0,
    limit: int = 1000,
    step: int = 1000,
):

    try:
        client_search: PubMedClient = PubMedClient()
        df_data = await client_search.colect_articleID(
            input_file="collect.csv",
            start=start,
            limit=limit,
            step=step,
        )

        output_stream = io.StringIO()

        df_data.to_csv(output_stream, index=False)
        output_stream.seek(0)

        return StreamingResponse(
            output_stream,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=pubmed_ids.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de Servidor: {str(e)}")


async def start_collect_abstract(
    start: int = 0,
    limit: int = 1000,
    max_threads: int = 10,
    file_with_ids: UploadFile = File(...),
):
    try:
        client_search: PubMedClient = PubMedClient(max_threads=max_threads)

        output_stream = io.StringIO()

        if file_with_ids.size <= 0 or file_with_ids is None:
            raise HTTPException(status_code=400, detail="Arquivo vazio!")

        df_result: pd.DataFrame = await client_search.collect_abstract(
            input_file=file_with_ids,
            start=start,
            limit=limit,
        )

        df_result.to_csv(output_stream, index=False)

        output_stream.seek(0)

        return StreamingResponse(
            output_stream,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=pubmed_abstracts.csv"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Servidor! Erro: {str(e)}")
