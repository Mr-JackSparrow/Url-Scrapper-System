from sqlalchemy import Column, String, UUID, text

from src.models.base import Base

class Dev(Base):

    __tablename__ = "dev"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    dev = Column(String(512), nullable = False)