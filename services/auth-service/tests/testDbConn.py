import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from src.dependencies import getDb
from src.models.base import Base
from sqlalchemy import text



def testDbConn():

    db : Session = next(getDb())

    try:
        result = db.execute(text("SELECT NOW();"))
        timestamp = result.fetchone()

        print("timestamp : ", timestamp)
        print("Base :: ", Base.metadata.tables.keys())
    finally:
        db.close()
