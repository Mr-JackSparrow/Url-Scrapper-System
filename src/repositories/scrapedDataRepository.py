from src.logging_config import setup_logging
import logging
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from src.models.scrapedDataModel import ScrapedData
from src.models.userModel import User
from src.dependencies import getDb

setup_logging()
log = logging.getLogger(__name__)

class ScrapedDataRepository:
    
    def __init__(self, db : Session):

        self.db = db

    def create_scraped_data(self, data : ScrapedData):
        
        try:
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)

            log.info(f"Successfully created scraped data record for URL: {data.url}")

        except HTTPException as hte:
            log.error(f"HTTPException Error at repository level : creating scraped data record for URL: {data.url}. Error: {str(hte)}")
            raise hte
        except Exception as e:
            self.db.rollback()
            log.error(f"Error at repository level creating scraped data record for URL: {data.url}. Error: {e}")
            raise e

    def create_scraped_data_batch(self, data_list: list[ScrapedData]):
        try:
            self.db.add_all(data_list)
            self.db.commit()

            log.info(f"Successfully created {len(data_list)} scraped data records in batch")
        except Exception as e:
            self.db.rollback()
            log.error(f"Error at repository level : creating batch scraped data records. Error: {e}")
            raise e
    
    def get_all_scraped_data(self, emailId, temp_token):
        try:
            scrapedData = (
                self.db.query(ScrapedData)
                .join(User, User.id == ScrapedData.user_id)
                .filter(User.email == emailId)
                .filter(ScrapedData.temp_token == temp_token)
                .all()
                )

            log.info(f"Successfully fetched {len(scrapedData)} scraped data records for email: {emailId}")

            return scrapedData
        
        except Exception as e:
            self.db.rollback()
            log.error(f"Error at repository level : fetching scraped data for email: {emailId}. Error: {e}")
            raise e