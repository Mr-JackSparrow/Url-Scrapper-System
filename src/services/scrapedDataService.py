from src.repositories.scrapedDataRepository import ScrapedDataRepository
from sqlalchemy.orm import Session
from fastapi import Depends
from src.dependencies import getDb
import os

class ScrapedDataService:

    def __init__(self, db : Session = Depends(getDb)):
        
        self.scrapedDataRepository = ScrapedDataRepository(db)
    

    def fetchAndSaveData(self, emailId):

        scrapedData = self.scrapedDataRepository.get_all_scraped_data(emailId)
        file_dir = "files"  
        os.makedirs(file_dir, exist_ok=True)  
        file_path = os.path.join(file_dir, "result.txt")  
    
        with open(file_path, "w", encoding="utf-8") as file:
            for data in scrapedData:
                file.write(f"Id: {data.id}\n")
                file.write(f"User-Id: {data.user_id}\n")
                file.write(f"User-Email-Id : {emailId}\n")
                file.write(f"URL: {data.url}\n")
                file.write(f"Title: {data.title}\n")
                file.write(f"Description: {data.description}\n")
                file.write(f"Keywords: {data.keywords}\n")
                file.write(f"Status: {data.status}\n")
                file.write(f"Error Message: {data.error_message}\n")
                file.write("-" * 50 + "\n")
    
        return file_path
    