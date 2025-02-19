from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.devModel import Dev

class DevRepository:

    def __init__(self, db : Session):

        self.db = db

    def get(self):

        try:

            result = self.db.query(Dev).all()
            return result
        except Exception as e:
            
            raise e
        
    def put(self, dev : Dev):
        
        try:

            self.db.add(dev)
            self.db.commit()
            self.db.refresh(dev)

            return dev.id
        except Exception as e:
            
            self.db.rollback()
            raise e