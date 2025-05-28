from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Import from session module to use PostgreSQL configuration
from ..db.session import Base, SessionLocal


# Definizione del modello User
class User(Base):
    __tablename__ = "auth_users"  # Rename to avoid conflicts with Users service table

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "parent", "child", "professional", "admin"