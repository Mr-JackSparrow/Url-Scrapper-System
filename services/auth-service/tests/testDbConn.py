import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from src.dependencies import getDb
from sqlalchemy import text



def testDbConn():

    db : Session = next(getDb())

    try:
        result = db.execute(text("SELECT NOW();"))
        timestamp = result.fetchone()

        print("timestamp : ", timestamp)
    finally:
        db.close()
