from fastapi import FastAPI
from src.api.routes.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router, tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Url Scraper"}