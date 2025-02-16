from src.core.database import SessionLocal

def getDb():
    
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()