from sqlalchemy import Column, UUID, String, TIMESTAMP, text
from src.models.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String(255), unique = True, nullable = False)
    password = Column(String(255), unique = True, nullable = False)
    created_at = Column(TIMESTAMP, server_default = text("CURRENT_TIMESTAMP"))