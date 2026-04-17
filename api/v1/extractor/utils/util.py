import io

from fastapi import UploadFile


async def convert_upload_files_to_tempdata(updload_file: UploadFile) -> io.StringIO:
    try:
        content_upload_file = await updload_file.read()
        decoded_content = content_upload_file.decode("utf-8")

        data_content = io.StringIO(decoded_content)
        return data_content

    except:
        raise Exception("Não foi possivel ler os dados do Arquivo!")
