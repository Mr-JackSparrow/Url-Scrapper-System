from src.repositories.userRepository import UserRepository
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.models.userModel import User
from sqlalchemy.orm import Session
from fastapi import Depends
from src.dependencies import getDb
from src.core.security import hash_password, verify_password

class UserService:


    def __init__(self, db : Session = Depends(getDb)):
        self.userRepository = UserRepository(db)

    def createUser(self, user : UserSchema):
        try:
            user_data = user.model_dump()
            if user_data["email"] in self.userRepository.getAllEmails():
                raise ValueError("Email already exists")
            user_data["password"] = hash_password(user_data["password"])
            del user_data["confirmPassword"]

            user : User = User(**user_data)
            return self.userRepository.createUser(user)
        except Exception as e:
            raise e
        
    def authenticate(self, user : UserLoginSchema) -> True:
        
        try:
            userData = user.model_dump()

            if not userData["email"] in self.userRepository.getAllEmails():
                raise ValueError("Email does not exists")
            
            resultUser = UserLoginSchema.model_validate(self.userRepository.getUserByEmailId(userData["email"])).model_dump()

            if not verify_password(userData["password"], resultUser["password"]):
                raise ValueError("Password is not same")

            return resultUser
        except Exception as e:
            raise e

            





        

