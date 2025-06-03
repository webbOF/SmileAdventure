# Users/src/services/user_service.py
# Implementazione del servizio per la gestione degli utenti, professionisti e specialità

from typing import List, Optional

# Placeholder for password hashing utility
# You should replace this with your actual password hashing implementation
# For example, importing it from a shared utility or the Auth service's utilities
from passlib.context import CryptContext
from sqlalchemy import func as sqlalchemy_func  # Renamed to avoid conflict
from sqlalchemy.orm import Session, joinedload
# Assuming schemas are in user_model.py as per previous steps
from src.models.user_model import (Child, ChildCreate, ChildUpdate, 
                                   ProfessionalCreate, ProfessionalUpdate,
                                   SensoryProfile, SensoryProfileCreate, SensoryProfileUpdate,
                                   Specialty, SpecialtyCreate, SpecialtyUpdate,
                                   User, UserCreate, UserType, UserUpdate,
                                   user_specialty_association)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Helper function to get specialty objects from IDs
def _get_specialty_objects(db: Session, specialty_ids: List[int]) -> List[Specialty]:
    if not specialty_ids:
        return []
    return db.query(Specialty).filter(Specialty.id.in_(specialty_ids)).all()

# User CRUD operations
def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = hash_password(user_data.password)
    # Ensure all fields from UserCreate are mapped to User model
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        surname=user_data.surname,
        user_type=user_data.user_type,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        phone=user_data.phone,
        address=user_data.address, # Assuming User model has address
        # city, postal_code, country might be in UserCreate or handled differently
        # For now, assuming they are part of UserCreate and User model
        city=getattr(user_data, 'city', None),
        postal_code=getattr(user_data, 'postal_code', None),
        country=getattr(user_data, 'country', 'Italia'),
        hashed_password=hashed_password # Add this if not already in User model
        # is_verified and is_active will use default values from the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_with_id(db: Session, user_data: UserCreate, user_id: int) -> User:
    """Create a user with a specific ID for Auth service synchronization."""
    hashed_password = hash_password(user_data.password)
    db_user = User(
        id=user_id,  # Set specific ID
        email=user_data.email,
        name=user_data.name,
        surname=user_data.surname,
        user_type=user_data.user_type,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        phone=user_data.phone,
        address=user_data.address,
        city=getattr(user_data, 'city', None),
        postal_code=getattr(user_data, 'postal_code', None),
        country=getattr(user_data, 'country', 'Italia'),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_professional(db: Session, professional_data: ProfessionalCreate) -> User:
    hashed_password = hash_password(professional_data.password)
    db_professional = User(
        email=professional_data.email,
        name=professional_data.name,
        surname=professional_data.surname,
        user_type=UserType.professional, # Ensure user_type is set to professional
        gender=professional_data.gender,
        birth_date=professional_data.birth_date,
        phone=professional_data.phone,
        address=professional_data.address, # Assuming User model has address
        city=getattr(professional_data, 'city', None),
        postal_code=getattr(professional_data, 'postal_code', None),
        country=getattr(professional_data, 'country', 'Italia'),
        hashed_password=hashed_password, # Add this
        bio=professional_data.bio,
        experience_years=professional_data.experience_years
    )
    
    if professional_data.specialties:
        specialty_objects = _get_specialty_objects(db, professional_data.specialties)
        db_professional.specialties.extend(specialty_objects)
        
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    return db_professional

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, user_type: Optional[UserType] = None) -> List[User]:
    query = db.query(User)
    if user_type:
        query = query.filter(User.user_type == user_type)
    return query.offset(skip).limit(limit).all()

def get_professionals(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    specialty_name: Optional[str] = None, 
    location_city: Optional[str] = None, 
    min_rating: Optional[float] = None
) -> List[User]:
    query = db.query(User).filter(User.user_type == UserType.professional)
    
    if specialty_name:
        # Ensure correct join for filtering by specialty name
        query = query.join(user_specialty_association).join(Specialty).filter(Specialty.name == specialty_name)
        
    if location_city:
        query = query.filter(sqlalchemy_func.lower(User.city) == sqlalchemy_func.lower(location_city))
        
    if min_rating is not None:
        query = query.filter(User.rating >= min_rating) # Assuming User model has 'rating'
        
    # Eager load specialties to avoid N+1 queries when accessing them
    return query.options(joinedload(User.specialties)).offset(skip).limit(limit).all()

def get_professional(db: Session, professional_id: int) -> Optional[User]:
    """Recupera un professionista specifico per ID."""
    return db.query(User).filter(
        User.id == professional_id, 
        User.user_type == UserType.professional
    ).options(joinedload(User.specialties)).first()

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user) # or db.merge(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_professional(db: Session, professional_id: int, professional_data: ProfessionalUpdate) -> Optional[User]:
    # Ensure we are fetching a user of type 'professional'
    db_professional = db.query(User).filter(User.id == professional_id, User.user_type == UserType.professional).first()
    if not db_professional:
        return None
        
    update_data = professional_data.model_dump(exclude_unset=True)
    
    if "specialties" in update_data and update_data["specialties"] is not None:
        specialty_ids = update_data.pop("specialties")
        # Efficiently update specialties
        db_professional.specialties.clear() 
        if specialty_ids:
            specialty_objects = _get_specialty_objects(db, specialty_ids)
            db_professional.specialties.extend(specialty_objects)
            
    for key, value in update_data.items():
        setattr(db_professional, key, value)
        
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    return db_professional

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user # The object is now detached and marked as deleted.

# Specialty CRUD operations
def create_specialty(db: Session, specialty_data: SpecialtyCreate) -> Specialty:
    db_specialty = Specialty(name=specialty_data.name, description=specialty_data.description)
    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)
    return db_specialty

def get_specialty(db: Session, specialty_id: int) -> Optional[Specialty]:
    return db.query(Specialty).filter(Specialty.id == specialty_id).first()

def get_specialty_by_name(db: Session, name: str) -> Optional[Specialty]:
    return db.query(Specialty).filter(Specialty.name == name).first()

def get_specialties(db: Session, skip: int = 0, limit: int = 100) -> List[Specialty]:
    return db.query(Specialty).offset(skip).limit(limit).all()

def update_specialty(db: Session, specialty_id: int, specialty_data: SpecialtyUpdate) -> Optional[Specialty]:
    db_specialty = get_specialty(db, specialty_id)
    if not db_specialty:
        return None
    
    update_data = specialty_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_specialty, key, value)
        
    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)
    return db_specialty

def delete_specialty(db: Session, specialty_id: int) -> Optional[Specialty]:
    db_specialty = get_specialty(db, specialty_id)
    if not db_specialty:
        return None
    db.delete(db_specialty)
    db.commit()
    return db_specialty

# Child CRUD operations
def create_child(db: Session, child_data: ChildCreate) -> Child:
    """Create a new child profile."""
    db_child = Child(
        name=child_data.name,
        surname=child_data.surname,
        birth_date=child_data.birth_date,
        diagnosis=child_data.diagnosis,
        parent_id=child_data.parent_id,
        sensory_preferences=child_data.sensory_preferences,
        communication_preferences=child_data.communication_preferences,
        behavioral_notes=child_data.behavioral_notes,
        support_level=child_data.support_level
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

def get_child(db: Session, child_id: int) -> Optional[Child]:
    """Get a child by ID."""
    return db.query(Child).filter(Child.id == child_id).first()

def get_children_by_parent(db: Session, parent_id: int, skip: int = 0, limit: int = 100) -> List[Child]:
    """Get all children for a specific parent."""
    return db.query(Child).filter(Child.parent_id == parent_id).offset(skip).limit(limit).all()

def get_children(db: Session, skip: int = 0, limit: int = 100) -> List[Child]:
    """Get all children (admin function)."""
    return db.query(Child).offset(skip).limit(limit).all()

def update_child(db: Session, child_id: int, child_data: ChildUpdate) -> Optional[Child]:
    """Update a child profile."""
    db_child = get_child(db, child_id)
    if not db_child:
        return None
    
    update_data = child_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_child, key, value)
        
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

def delete_child(db: Session, child_id: int) -> Optional[Child]:
    """Delete a child profile."""
    db_child = get_child(db, child_id)
    if not db_child:
        return None
    db.delete(db_child)
    db.commit()
    return db_child

# Sensory Profile CRUD operations
def create_sensory_profile(db: Session, sensory_profile_data: SensoryProfileCreate) -> SensoryProfile:
    """Create a new sensory profile."""
    db_sensory_profile = SensoryProfile(**sensory_profile_data.model_dump())
    db.add(db_sensory_profile)
    db.commit()
    db.refresh(db_sensory_profile)
    return db_sensory_profile

def get_sensory_profile(db: Session, sensory_profile_id: int) -> Optional[SensoryProfile]:
    """Get a sensory profile by ID."""
    return db.query(SensoryProfile).filter(SensoryProfile.id == sensory_profile_id).first()

def get_sensory_profile_by_child(db: Session, child_id: int) -> Optional[SensoryProfile]:
    """Get a sensory profile by child ID."""
    return db.query(SensoryProfile).filter(SensoryProfile.child_id == child_id).first()

def get_sensory_profiles(db: Session, skip: int = 0, limit: int = 100) -> List[SensoryProfile]:
    """Get list of all sensory profiles."""
    return db.query(SensoryProfile).offset(skip).limit(limit).all()

def update_sensory_profile(db: Session, sensory_profile_id: int, sensory_profile_data: SensoryProfileUpdate) -> Optional[SensoryProfile]:
    """Update a sensory profile."""
    db_sensory_profile = get_sensory_profile(db, sensory_profile_id)
    if not db_sensory_profile:
        return None
        
    update_data = sensory_profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sensory_profile, key, value)
        
    db.add(db_sensory_profile)
    db.commit()
    db.refresh(db_sensory_profile)
    return db_sensory_profile

def delete_sensory_profile(db: Session, sensory_profile_id: int) -> Optional[SensoryProfile]:
    """Delete a sensory profile."""
    db_sensory_profile = get_sensory_profile(db, sensory_profile_id)
    if not db_sensory_profile:
        return None
    db.delete(db_sensory_profile)
    db.commit()
    return db_sensory_profile