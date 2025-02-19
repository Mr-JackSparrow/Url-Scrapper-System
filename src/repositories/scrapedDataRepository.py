from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from src.models.scrapedDataModel import ScrapedData
from src.models.userModel import User
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

    def create_scraped_data_batch(self, data_list: list[ScrapedData]):
        try:
            self.db.add_all(data_list)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_all_scraped_data(self, emailId):
        try:
            
            return self.db.query(ScrapedData).join(User, User.id == ScrapedData.user_id).filter(User.email == emailId).all()

        except Exception as e:
            self.db.rollback()
            raise e