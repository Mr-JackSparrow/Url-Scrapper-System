from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.services.userService import UserService
from src.core.security import create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserSchema, service : UserService = Depends(UserService)):
    try:
        usern = service.createUser(user)
        return {"message": f"User created with user = {usern}"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise e

@router.post("/login")
async def login(user: UserLoginSchema, service : UserService = Depends(UserService)):
    try:
        authenticatedUser : dict = service.authenticate(user)

        if not authenticatedUser:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"sub": authenticatedUser["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")