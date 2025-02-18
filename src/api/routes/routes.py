from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from src.schemas.userRegisterSchema import UserSchema
from src.schemas.userLoginSchema import UserLoginSchema
from src.services.userService import UserService
from src.core.security import create_access_token, decode_token
from pandas import read_csv
from src.core.celerySetup import celeryApp

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user : UserSchema, service : UserService = Depends(UserService)):
    try:
        usern = service.createUser(user)
        return {"message": f"User created with user = {usern}"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise e

@router.post("/login")
async def login(request : Request, user: UserLoginSchema, service : UserService = Depends(UserService)):
    try:

        token = request.headers.get("Authorization")

        if token:
            try:
                decode_token(token.split("Bearer ")[-1])
                return {"message": "Already logged in"}
            except Exception:
                pass

        authenticatedUser : dict = service.authenticate(user)

        if not authenticatedUser:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"sub": authenticatedUser["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}")
    

@router.post("/upload-csv/")
async def upload_csv(file : UploadFile = File(...)):

    if file.content_type != "text/csv":
        return HTTPException(status_code = 400, detail = "File must be a CSV file")
    
    urlList : list = read_csv(file.file).values.tolist()

    urlList : list = [url[0] for url in urlList]

    task = celeryApp.send_task('scrapper-service.core.celerySetup.scrapMetaData', args=[urlList])

    return {"urlList" : task.id}


@router.get("/get-meta-data/{task_id}")
async def get_meta_data(task_id : str):
    task = celeryApp.AsyncResult(task_id)
    return {"status" : task.state}

