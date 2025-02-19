from sqlalchemy import Column, UUID, String, ForeignKey, text
from src.models.base import Base

class ScrapedData(Base):
    __tablename__ = "scraped_data"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    temp_token = Column(String(512), nullable=False)
    url = Column(String(512), nullable=False)
    title = Column(String(512), nullable=True)
    description = Column(String(1024), nullable=True)
    keywords = Column(String(1024), nullable=True)
    status = Column(String(50), nullable=True)  
    error_message = Column(String(1024), nullable=True) 

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)