import os
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from src.services.scrapedDataService import ScrapedDataService
from src.core.security import validate_token
from pandas import read_csv
from src.core.celerySetup import celeryApp

scraperRouter = APIRouter()
    
@scraperRouter.post("/upload-csv/")
async def upload_csv(file : UploadFile = File(...), payload = Depends(validate_token)):
    
    emailId = payload.get("email")

    if file.content_type != "text/csv":
        return HTTPException(status_code = 400, detail = "File must be a CSV file")
    
    urlList : list = read_csv(file.file).values.tolist()

    urlList : list = [url[0] for url in urlList]

    task = celeryApp.send_task('scrapper-service.core.celerySetup.scrapMetaData', args=[urlList, emailId])

    return {"urlList" : task.id}


@scraperRouter.get("/check-status/{task_id}")
async def checkStatus(task_id : str, service: ScrapedDataService = Depends(ScrapedDataService), tokenData = Depends(validate_token)):

    task = celeryApp.AsyncResult(task_id)
    return {"status" : task.state}

@scraperRouter.get("/download-scraped-data")
async def download_scraped_data(service: ScrapedDataService = Depends(ScrapedDataService), payload = Depends(validate_token)):

    emailId = payload.get("email")

    file_path = None
    try:
        file_path = service.fetchAndSaveData(emailId)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        response = FileResponse(
            path=file_path,
            filename="result.txt",
            media_type="text/plain",
        )

        async def delete_file_after_response():
            if os.path.exists(file_path):
                os.remove(file_path)
        response.background = delete_file_after_response

        return response
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

