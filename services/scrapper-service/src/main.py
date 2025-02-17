from fastapi import FastAPI
from src.api.routes.scrapperRoutes import router


app = FastAPI()

app.include_router(router = router)

