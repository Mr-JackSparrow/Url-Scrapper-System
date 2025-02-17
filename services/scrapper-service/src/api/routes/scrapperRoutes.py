from fastapi import APIRouter, File, UploadFile, HTTPException
from pandas import read_csv
from src.core.celerySetup import celeryApp


router = APIRouter()


@router.post("/upload-csv/")
async def upload_csv(file : UploadFile = File(...)):

    if file.content_type != "text/csv":
        return HTTPException(status_code = 400, detail = "File must be a CSV file")
    
    urlList : list = read_csv(file.file).values.tolist()

    urlList : list = [url[0] for url in urlList]

    task = celeryApp.send_task('scrapper-service.core.celerySetup.scrapMetaData', args=[urlList])

    return {"urlList" : task.id}


@router.get("/get-meta-data/{task_id}")
async def get_meta_data(task_id : str):
    task = celeryApp.AsyncResult(task_id)
    return {"status" : task.state}