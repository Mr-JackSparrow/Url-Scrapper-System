from fastapi import FastAPI
from src.api.routes.scraperRoutes import scraperRouter
from src.api.routes.authRoutes import authRouter
from src.api.routes.stayAwake import awakeRouter
app = FastAPI()

app.include_router(authRouter, tags = ["auth"])
app.include_router(scraperRouter, tags = ["scraper"])
app.include_router(awakeRouter, prefix = "/dev")

@app.get("/")
def read_root():
    return {"message": "Welcome to Url Scraper"}