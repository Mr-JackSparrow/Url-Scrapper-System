from fastapi import FastAPI
from src.api.routes.routes import router as auth_router

# Create the FastAPI app
app = FastAPI()

# Include the router
app.include_router(auth_router, tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Auth Service"}