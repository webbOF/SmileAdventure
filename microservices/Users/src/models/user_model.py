from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Table, Text, JSON)
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
    hashed_password = Column(String, nullable=False)
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

# Child model for storing child profiles
class Child(Base):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    diagnosis = Column(String, nullable=True)  # ASD diagnosis information
    parent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # ASD-specific fields
    sensory_preferences = Column(JSON, nullable=True)  # JSON field for sensory preferences
    communication_preferences = Column(JSON, nullable=True)  # Communication style preferences
    behavioral_notes = Column(Text, nullable=True)  # Notes about behavioral patterns
    support_level = Column(Integer, nullable=True)  # ASD support level (1-3)
      # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("User", backref="children")
    sensory_profile = relationship("SensoryProfile", back_populates="child", uselist=False)

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

# Child Pydantic schemas
class ChildBase(BaseModel):
    name: str
    surname: str
    birth_date: str  # Format: YYYY-MM-DD
    diagnosis: Optional[str] = None
    parent_id: int
    sensory_preferences: Optional[Dict[str, Any]] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    behavioral_notes: Optional[str] = None
    support_level: Optional[int] = Field(None, ge=1, le=3)

class ChildCreate(ChildBase):
    pass

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    birth_date: Optional[str] = None
    diagnosis: Optional[str] = None
    sensory_preferences: Optional[Dict[str, Any]] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    behavioral_notes: Optional[str] = None
    support_level: Optional[int] = Field(None, ge=1, le=3)

class ChildInDB(ChildBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
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

# Sensory Profile Model (SQLAlchemy)
class SensoryProfile(Base):
    __tablename__ = "sensory_profiles"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey('children.id'), nullable=False)
    visual_sensitivity = Column(Integer, nullable=True)  # 1-5 scale
    auditory_sensitivity = Column(Integer, nullable=True)  # 1-5 scale
    tactile_sensitivity = Column(Integer, nullable=True)  # 1-5 scale
    proprioceptive_needs = Column(Integer, nullable=True)  # 1-5 scale
    vestibular_preferences = Column(Integer, nullable=True)  # 1-5 scale
    adaptation_strategies = Column(JSON, nullable=True)  # Array of strategies
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to child
    child = relationship("Child", back_populates="sensory_profile")

# Sensory Profile Pydantic Schemas
class SensoryProfileBase(BaseModel):
    child_id: int
    visual_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    auditory_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    tactile_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    proprioceptive_needs: Optional[int] = Field(None, ge=1, le=5)
    vestibular_preferences: Optional[int] = Field(None, ge=1, le=5)
    adaptation_strategies: Optional[List[str]] = None

class SensoryProfileCreate(SensoryProfileBase):
    pass

class SensoryProfileUpdate(BaseModel):
    visual_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    auditory_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    tactile_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    proprioceptive_needs: Optional[int] = Field(None, ge=1, le=5)
    vestibular_preferences: Optional[int] = Field(None, ge=1, le=5)
    adaptation_strategies: Optional[List[str]] = None

class SensoryProfileInDB(SensoryProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True