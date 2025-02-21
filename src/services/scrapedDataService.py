from src.logging_config import setup_logging
import logging
from src.repositories.scrapedDataRepository import ScrapedDataRepository
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from src.dependencies import getDb
import os

setup_logging()
log = logging.getLogger(__name__)

class ScrapedDataService:

    def __init__(self, db : Session = Depends(getDb)):
        self.scrapedDataRepository = ScrapedDataRepository(db)
    

    def fetchAndSaveData(self, emailId, temp_token):
        try:
            scrapedData = self.scrapedDataRepository.get_all_scraped_data(emailId, temp_token)
            if not scrapedData:
                log.error("Error at service level in fetchAndSaveData: No data found for the given Task ID")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the given Task ID")

            file_dir = "files"  
            os.makedirs(file_dir, exist_ok=True)  
            file_path = os.path.join(file_dir, "result.txt")  
        
            with open(file_path, "w", encoding="utf-8") as file:
                for data in scrapedData:
                    file.write(f"Id: {data.id}\n")
                    file.write(f"User-Id: {data.user_id}\n")
                    file.write(f"User-Email-Id : {emailId}\n")
                    file.write(f"Temp-Token: {data.temp_token}\n")
                    file.write(f"URL: {data.url}\n")
                    file.write(f"Title: {data.title}\n")
                    file.write(f"Description: {data.description}\n")
                    file.write(f"Keywords: {data.keywords}\n")
                    file.write(f"Status: {data.status}\n")
                    file.write(f"Error Message: {data.error_message}\n")
                    file.write("-" * 50 + "\n")
        
            return file_path
        
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            log.error(f"Error at service level in fetchAndSaveData: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while fetching and saving data")