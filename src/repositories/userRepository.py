from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import select
from src.models.userModel import User
from src.dependencies import getDb

class UserRepository:

    def __init__(self, db : Session):

        self.db = db

    def getAllEmails(self) -> set:
        try:
            result = self.db.execute(select(User.email))
            return {row[0] for row in result.fetchall()}
        except Exception as e:
            raise e

    def createUser(self, user: User):
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user.id
        except Exception as e:
            self.db.rollback()
            raise e
        
    def getUserByEmailId(self, email : str):
        try:
            result = self.db.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except Exception as e:
            raise e