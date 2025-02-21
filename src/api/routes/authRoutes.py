from src.logging_config import setup_logging
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.services.userService import UserService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.security import create_access_token, validate_token

setup_logging()
log = logging.getLogger(__name__)

authRouter = APIRouter()

@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user : UserSchema, service : UserService = Depends(UserService)):
    try:
        usern = service.createUser(user)
        access_token = create_access_token(data={"email": user.email})

        result = {
            "access_token": access_token,
            "token_type": "bearer",
            "message": f"User created with user = {usern}"
        }
    
        return {"result": result}
    except ValueError as e:
        log.error(f"ValueError at controller level  in /register : {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as htre:
        log.error(f"HttpExceptionError at controller level in /register: {htre.detail}")
        raise htre
    except Exception as e:
        log.error(f"Error at controller level in /register: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
    
security = HTTPBearer(auto_error=False)

@authRouter.post("/login")
async def login(
    request: Request,
    user: UserLoginSchema,
    service: UserService = Depends(UserService),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    try:
        token = credentials.credentials if isinstance(credentials, HTTPAuthorizationCredentials) else None
        log.warning(f"Received token: {type(token)}")

        log.warning(f"before payload")
        
        if token == None:
            pass
        else:
            payload = validate_token(credentials)
            log.warning(f"Error at controller level : User {payload['email']} already logged in")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {payload['email']} already logged in",
            )

        authenticatedUser: dict = service.authenticate(user)
        if not authenticatedUser:
            log.warning(f"Error at controller level : Authentication failed for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        access_token = create_access_token(data={"email": authenticatedUser["email"]})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException as hte:
        log.error(f"HTTPExceptionError at controller level : {hte.detail}")
        raise hte

    except Exception as e:
        log.error(f"Unexpected Error at controller level in /login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )