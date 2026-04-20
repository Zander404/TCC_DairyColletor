import io
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile

from api.v1.modelo.services import ModeloServices


routers = APIRouter()


def get_services():
    return ModeloServices()


ServicesDep = Annotated[ModeloServices, Depends(get_services)]


@routers.post("/execute_model")
async def execute_model(services: ServicesDep, input_file: UploadFile):
    input_content = await input_file.read()

    content_decoded = input_content.decode("utf-8")
    bytes_content = io.StringIO(content_decoded)

    return services.execute_agent(
        input_content=bytes_content,
        result_file_name="teste",
        agent="GPT",
        model="gpt-4",
    )


@routers.post("/execute_test")
async def execute_test(services: ServicesDep):
    return services.execute_evaluation()
