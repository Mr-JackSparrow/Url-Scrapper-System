from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from src.models.scrapedDataModel import ScrapedData
from src.dependencies import getDb

class ScrapedDataRepository:
    
    def __init__(self, db : Session):

        self.db = db

    def create_scraped_data(self, data : ScrapedData):
        
        try:
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
        except Exception as e:
            self.db.rollback()
            raise e
