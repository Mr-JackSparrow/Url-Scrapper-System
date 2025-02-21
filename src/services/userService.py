from src.logging_config import setup_logging
import logging
from src.repositories.userRepository import UserRepository
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.models.userModel import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from src.dependencies import getDb
from src.core.security import hash_password, verify_password

setup_logging()
log = logging.getLogger(__name__)
class UserService:

    def __init__(self, db : Session = Depends(getDb)):
        self.userRepository = UserRepository(db)

    def createUser(self, user : UserSchema):
        try:
            user_data = user.model_dump()
            if user_data["email"] in self.userRepository.getAllEmails():
                log.error("Error as service level Email already exists")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
            
            user_data["password"] = hash_password(user_data["password"])
            del user_data["confirmPassword"]

            user : User = User(**user_data)
            return self.userRepository.createUser(user)
        
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            log.error(f"Error as service level Error in createUser: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while creating the user")
        
    def getUserId(self, emailId : str):
        try:
            userId = self.userRepository.getUserIdByEmailId(emailId)
            if not userId:
                log.error("Error as service level User not found")
                raise HTTPException(status_code=404, detail="User not found")
            return userId
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            log.error(f"Error as service level while fetching getUserId: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while fetching the user ID")
    
    def authenticate(self, user : UserLoginSchema) -> True:
        try:
            userData = user.model_dump()

            if not userData["email"] in self.userRepository.getAllEmails():
                log.error("Error as service level Email does not exist")
                raise HTTPException(status_code=404, detail="Email does not exist")
            
            resultUser = UserLoginSchema.model_validate(self.userRepository.getUserByEmailId(userData["email"])).model_dump()

            if not verify_password(userData["password"], resultUser["password"]):
                log.error("Error as service level Incorrect password")
                raise HTTPException(status_code=401, detail="Incorrect password")

            return resultUser
        
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            log.error(f"Error as service level in authenticate: {e}")
            raise HTTPException(status_code=500, detail="An error occurred during authentication")

        