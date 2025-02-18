from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import getDbSettings

settings = getDbSettings()

engine = create_engine(settings.DBURL)
SessionLocal = sessionmaker(autoflush = False, bind = engine)

