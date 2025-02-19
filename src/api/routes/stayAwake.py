from fastapi import APIRouter, Header, HTTPException, Depends
from src.services.devService import DevService

awakeRouter = APIRouter()


@awakeRouter.get("/stay-awake", include_in_schema=False)
async def stayAwake(header : str = Header(None), service : DevService = Depends(DevService)):
    
    try:
        if header != "devOnly":
            raise HTTPException(status_code=403, 
            detail="Forbidden: Invalid Header")
        
        result = service.get()
        return {"message" : f"{result}"}
    except Exception as e:
        raise e
    

@awakeRouter.get("/stay-awake/put", include_in_schema=False)
async def stayAwakePut(header : str = Header(None), service : DevService = Depends(DevService)):
    
    try:
        if header != "devOnly":
            raise HTTPException(status_code=403, 
            detail="Forbidden: Invalid Header")
        
        id = service.put("DevOnly")

        return {"id" : f"{id}"}
    except Exception as e:
        raise e