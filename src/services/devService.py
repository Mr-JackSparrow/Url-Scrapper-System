from src.repositories.devRepository import DevRepository
from sqlalchemy.orm import Session
from src.models.devModel import Dev
from fastapi import Depends
from src.dependencies import getDb


class DevService:

    def __init__(self, db : Session = Depends(getDb)):
        self.repo = DevRepository(db)

    def put(self, data : str):

        try:

            dev = Dev()
            dev.dev = data

            return self.repo.put(dev)
        except Exception as e:
            raise e
        
    def get(self):

        try:

            result = self.repo.get()
            return [dev.dev for dev in result]
        except Exception as e:
            
            raise e

        
