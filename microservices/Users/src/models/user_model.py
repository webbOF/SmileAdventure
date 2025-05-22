from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Table, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enum per UserType
class UserType(str, Enum):
    child = "child"
    parent = "parent"
    professional = "professional"
    admin = "admin"

# Tabella di associazione per la relazione many-to-many tra utenti e specialità
user_specialty_association = Table(
    'user_specialty_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('specialty_id', Integer, ForeignKey('specialties.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    user_type = Column(String, nullable=False)  # 'client' o 'professional'
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    gender = Column(String(1), nullable=True)  # 'M', 'F', or 'O'
    birth_date = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True, default="Italia")
    profile_image = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campi specifici per professionisti
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True, default=0)
    
    # Relazioni
    specialties = relationship("Specialty", secondary=user_specialty_association, back_populates="professionals")

class Specialty(Base):
    __tablename__ = "specialties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relazioni
    professionals = relationship("User", secondary=user_specialty_association, back_populates="specialties")

# Schemi Pydantic
class SpecialtyBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpecialtyCreate(SpecialtyBase):
    pass

class SpecialtyUpdate(SpecialtyBase):
    pass

class SpecialtyInDB(SpecialtyBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: str
    surname: str
    user_type: UserType 
    gender: Optional[str] = Field(None, pattern="^[MFU]$") # M, F, Unknown/Unspecified
    birth_date: Optional[str] = None # Considerare Optional[date] con Pydantic v2
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "Italia"

class UserCreate(UserBase):
    password: str

class ProfessionalCreate(UserBase):
    password: str # Necessaria per la creazione dell'utente base
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    specialties: List[int] = []

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^[MFU]$")
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    profile_image: Optional[str] = None

class ProfessionalUpdate(UserUpdate):
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    specialties: Optional[List[int]] = None

class UserInDB(UserBase):
    id: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile_image: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProfessionalInDB(UserInDB):
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = None
    review_count: Optional[int] = None
    specialties: List[SpecialtyInDB] = []
    
    class Config:
        from_attributes = True