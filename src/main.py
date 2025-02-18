from fastapi import FastAPI
from src.api.routes.routes import router as auth_router

# Create the FastAPI app
app = FastAPI()

print("Auth Service is running")

# Include the router
app.include_router(auth_router, tags=["auth"])

@app.get("/")
def read_root():
    print("shubya bhikarchod")
    return {"message": "Auth Service"}