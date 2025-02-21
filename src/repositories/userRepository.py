from src.logging_config import setup_logging
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from src.models.userModel import User

setup_logging()
log = logging.getLogger(__name__)
class UserRepository:

    def __init__(self, db : Session):

        self.db = db

    def getAllEmails(self) -> set:
        try:
            result = self.db.execute(select(User.email))
            return {row[0] for row in result.fetchall()}
        except SQLAlchemyError as e:
            log.error(f"Database error at repository level in getAllEmails: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error while fetching emails")
        except Exception as e:
            log.error(f"Unexpected error at repository level in getAllEmails: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Unexpected error while fetching emails")

    def createUser(self, user: User):
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            log.info(f"Successfully created user with ID: {user.id}")
            return user.id
        except SQLAlchemyError as e:
            self.db.rollback()
            log.error(f"Database error at repository level in createUser: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error while creating user")
        except Exception as e:
            self.db.rollback()
            log.error(f"Unexpected error at repository level in createUser: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Unexpected error while creating user")

        
    def getUserByEmailId(self, email : str):
        try:
            result = self.db.execute(select(User).where(User.email == email))
            user = result.scalars().first()
            if not user:
                log.warning(f"Warning at repository level No user found with email: {email}")
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except SQLAlchemyError as e:
            log.error(f"Database error at repository level in getUserByEmailId: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error while fetching user")
        except Exception as e:
            log.error(f"Unexpected error at repository level in getUserByEmailId: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Unexpected error while fetching user")
        
    def getUserIdByEmailId(self, email : str):
        try:
            result = self.db.execute(select(User.id).where(User.email == email))
            user_id = result.scalars().first()
            if not user_id:
                log.warning(f"Warning at repository level No user found with email: {email}")
                raise HTTPException(status_code=404, detail="User not found")
            return user_id
        except SQLAlchemyError as e:
            log.error(f"Database error at repository level in getUserIdByEmailId: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error while fetching user ID")
        except Exception as e:
            log.error(f"Unexpected error at repository level in getUserIdByEmailId: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Unexpected error while fetching user ID")