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
        log.warning(f"Error at controller level: Invalid File Name in /upload-csv")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV file")

    content = await file.read()
    if not content:
        log.warning(f"Error at controller level: Empty file uploaded in /upload-csv")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty")

    file.file.seek(0)

    try:
        csv_data = io.StringIO(content.decode("utf-8"))
        reader = csv.reader(csv_data)

        try:
            header = next(reader)
        except StopIteration:
            log.warning(f"Error at controller level: Empty CSV file in /upload-csv")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty")

        if len(header) != 1 or header[0].strip().lower() != "url":
            log.warning(f"Error at controller level: Invalid CSV header in /upload-csv")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file must contain only one column named 'url' (case-insensitive)"
            )

        urlList = []
        for row in reader:
            if len(row) != 1:
                log.warning(f"Error at controller level: Invalid row format in /upload-csv")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each row in the CSV file must contain only one column"
                )
            url = row[0].strip()
            if url:
                urlList.append(url)

        if not urlList:
            log.warning(f"Error at controller level: No valid URLs found in /upload-csv")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file must contain at least one valid URL"
            )

    except HTTPException as hte:
        log.error(f"Error at controller level: Error parsing CSV file: {str(hte)}")
        raise hte
    except Exception as e:
        log.error(f"Error at controller level: Error parsing CSV file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV format")
    
    task = celeryApp.send_task('scrapper-service.core.celerySetup.scrapMetaData', args=[urlList, emailId])

    return {"task_id": task.id}

@scraperRouter.get("/check-status/{task_id}")
async def checkStatus(task_id: str, service: ScrapedDataService = Depends(ScrapedDataService), tokenData=Depends(validate_token)):
    try: 
        if not task_id or not task_id.strip():
            log.error(f"Error at controller level : Invalid Task Id in /check-status")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Task Id")
        task = celeryApp.AsyncResult(task_id)
        if not task:
            log.error(f"Error at controller level : Task not found in /check-status")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return {"status": task.state}
    except HTTPException as hte:
        raise hte
    except Exception as e:
        log.error(f"Error at controller level : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@scraperRouter.get("/download-scraped-data/{task_id}")
async def download_scraped_data(task_id: str, service: ScrapedDataService = Depends(ScrapedDataService), payload=Depends(validate_token)):
    emailId = payload.get("email")

    file_path = None
    try:
        task = celeryApp.AsyncResult(task_id)
        if task.state == "SUCCESS":
            file_path = service.fetchAndSaveData(emailId, task_id)
        else:
            log.error(f"Error at controller level : Task not completed in /download-scraped-data")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not completed")

        if not os.path.exists(file_path):
            log.error(f"Error at controller level : File not found in /download-scraped-data")
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
    except HTTPException as hte:
        raise hte
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        log.error(f"Unexpected Error in /download-scraped-data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    






    