from src.logging_config import setup_logging
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.services.userService import UserService
from src.core.security import create_access_token, validate_token

setup_logging()
log = logging.getLogger(__name__)

authRouter = APIRouter()

@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user : UserSchema, service : UserService = Depends(UserService)):
    try:
        usern = service.createUser(user)
        return {"message": f"User created with user = {usern}"}
    except ValueError as e:
        log.error(f"ValueError in /register : {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error in /register: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

@authRouter.post("/login")
async def login(request : Request, user: UserLoginSchema, service : UserService = Depends(UserService)):
    try:

        token = request.headers.get("Authorization")

        if token:
            try:
                validate_token(token.split("Bearer ")[-1])
                return {"message": "Already logged in"}
            except Exception:
                log.error(f"Token Error in /login : {e}")
                pass

        authenticatedUser : dict = service.authenticate(user)

        if not authenticatedUser:
            log.warning(f"Authentication failed for user : {user.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"email": authenticatedUser["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        log.error(f"Unexpected Error in /login : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")