from fastapi import APIRouter, Header, HTTPException

awakeRouter = APIRouter()


@awakeRouter.get("/stay-awake")
async def stayAwake(header : str = Header(None)):
    if header != "devOnly":
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Header")
    return {"message" : "dev only"}