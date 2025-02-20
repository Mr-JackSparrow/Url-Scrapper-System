import os, io, csv
from src.logging_config import setup_logging
import logging
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from pydantic import Field
from fastapi.responses import FileResponse
from src.services.scrapedDataService import ScrapedDataService
from src.core.security import validate_token
from src.core.celerySetup import celeryApp

setup_logging()
log = logging.getLogger(__name__)

scraperRouter = APIRouter()

@scraperRouter.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), payload=Depends(validate_token)):
    emailId = payload.get("email")

    if not file.filename.endswith(".csv"):
        log.warning(f"Invalid File Name in /upload-csv")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV file")
    
    content = await file.read()
    file.file.seek(0)

    try:
        csv_data = io.StringIO(content.decode("utf-8"))
        reader = csv.reader(csv_data)
        urlList = []
        next(reader)
        
        for row in reader:
            url = row[0].strip()
            urlList.append(url)

    except Exception as e:
        log.error(f"Error parsing CSV file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV format")

    task = celeryApp.send_task('scrapper-service.core.celerySetup.scrapMetaData', args=[urlList, emailId])

    return {"task_id": task.id}

@scraperRouter.get("/check-status/{task_id}")
async def checkStatus(task_id: str, service: ScrapedDataService = Depends(ScrapedDataService), tokenData=Depends(validate_token)):
    if not task_id or not task_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Task Id")
    task = celeryApp.AsyncResult(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"status": task.state}

@scraperRouter.get("/download-scraped-data/{task_id}")
async def download_scraped_data(task_id: str, service: ScrapedDataService = Depends(ScrapedDataService), payload=Depends(validate_token)):
    emailId = payload.get("email")

    file_path = None
    try:
        file_path = service.fetchAndSaveData(emailId, task_id)

        if not os.path.exists(file_path):
            log.error(f"File not found in /download-scraped-data")
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="File not found")
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
        log.error(f"Unexpected Error in /download-scraped-data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    






    