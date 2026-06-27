from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import os
from drive import get_files, upload_file, delete_file, download_file
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from drive import (
    download_file,
    get_file_name
)


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/files")
def read_files(request: Request):

    files = get_files()

    return templates.TemplateResponse(
        request=request,
        name="files.html",
        context={
            "files": files
        }
    )

@app.post("/upload")
def upload(uploaded_file: UploadFile = File(...)):

    upload_file(uploaded_file)

    return RedirectResponse(
        url="/files",
        status_code=303
    )

@app.get("/delete/{file_id}")
def delete(file_id: str):
    delete_file(file_id)

    return RedirectResponse(
        url="/files",
        status_code=303
    )

from fastapi.responses import StreamingResponse
from googleapiclient.discovery import build

@app.get("/download/{file_id}")
def download(file_id: str):

    file_stream = download_file(file_id)

    file_name = get_file_name(file_id)

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"'
        }
    )

