from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.models.user_model import (ProfessionalCreate, ProfessionalInDB,
                                   ProfessionalUpdate, SpecialtyCreate,
                                   SpecialtyInDB, SpecialtyUpdate, UserCreate,
                                   UserInDB, UserUpdate)
from src.services import user_service

router = APIRouter()

# Users endpoints
@router.post("/users/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crea un nuovo utente."""
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user_data=user)

@router.post("/professionals/", response_model=ProfessionalInDB)
def create_professional(professional: ProfessionalCreate, db: Session = Depends(get_db)):
    """Crea un nuovo professionista."""
    db_user = user_service.get_user_by_email(db, email=professional.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_professional(db=db, professional_data=professional)

@router.get("/users/", response_model=List[UserInDB])
def read_users(
    skip: int = Query(0), 
    limit: int = Query(100), 
    user_type: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Recupera l'elenco degli utenti o un utente specifico per email."""
    # If email is provided, return specific user
    if email:
        db_user = user_service.get_user_by_email(db, email=email)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return [db_user]  # Return as list to match the response model
    
    # Otherwise return list of users
    users = user_service.get_users(db, skip=skip, limit=limit, user_type=user_type)
    return users

@router.get("/users/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Recupera un utente specifico."""
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Aggiorna un utente esistente."""
    db_user = user_service.update_user(db, user_id=user_id, user_data=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina un utente."""
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Professionals endpoints
@router.get("/professionals/", response_model=List[ProfessionalInDB])
def read_professionals(
    skip: int = 0, 
    limit: int = 100,
    specialty: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Recupera l'elenco dei professionisti."""
    professionals = user_service.get_professionals(
        db, 
        skip=skip, 
        limit=limit, 
        specialty_name=specialty,  # Mapped to correct parameter
        location_city=location,    # Mapped to correct parameter
        min_rating=min_rating
    )
    return professionals

@router.get("/professionals/{professional_id}", response_model=ProfessionalInDB)
def read_professional(professional_id: int, db: Session = Depends(get_db)):
    """Recupera un professionista specifico."""
    db_professional = user_service.get_professional(db, professional_id=professional_id)
    if db_professional is None:
        raise HTTPException(status_code=404, detail="Professional not found")
    return db_professional

@router.put("/professionals/{professional_id}", response_model=ProfessionalInDB)
def update_professional(professional_id: int, professional: ProfessionalUpdate, db: Session = Depends(get_db)):
    """Aggiorna un professionista esistente."""
    db_professional = user_service.update_professional(db, professional_id=professional_id, professional_data=professional)
    if db_professional is None:
        raise HTTPException(status_code=404, detail="Professional not found")
    return db_professional

@router.get("/professionals/search", response_model=List[ProfessionalInDB])
def search_professionals(
    specialty: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    gender: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Cerca professionisti in base a vari criteri."""
    filters = {
        "specialty": specialty,
        "location": location,
        "min_rating": min_rating,
        "gender": gender
    }
    professionals = user_service.search_professionals(db, filters, skip=skip, limit=limit)
    return professionals

# Specialties endpoints
@router.post("/specialties/", response_model=SpecialtyInDB)
def create_specialty(specialty: SpecialtyCreate, db: Session = Depends(get_db)):
    """Crea una nuova specialità."""
    db_specialty = user_service.get_specialty_by_name(db, name=specialty.name)
    if db_specialty:
        raise HTTPException(status_code=400, detail="Specialty already exists")
    return user_service.create_specialty(db, specialty_data=specialty)

@router.get("/specialties/", response_model=List[SpecialtyInDB])
def read_specialties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Recupera l'elenco delle specialità."""
    specialties = user_service.get_specialties(db, skip=skip, limit=limit)
    return specialties

@router.get("/specialties/{specialty_id}", response_model=SpecialtyInDB)
def read_specialty(specialty_id: int, db: Session = Depends(get_db)):
    """Recupera una specialità specifica."""
    db_specialty = user_service.get_specialty(db, specialty_id=specialty_id)
    if db_specialty is None:
        raise HTTPException(status_code=404, detail="Specialty not found")
    return db_specialty

@router.put("/specialties/{specialty_id}", response_model=SpecialtyInDB)
def update_specialty(specialty_id: int, specialty: SpecialtyUpdate, db: Session = Depends(get_db)):
    """Aggiorna una specialità esistente."""
    db_specialty = user_service.update_specialty(
        db, 
        specialty_id=specialty_id, 
        name=specialty.name, 
        description=specialty.description
    )
    if db_specialty is None:
        raise HTTPException(status_code=404, detail="Specialty not found")
    return db_specialty

@router.delete("/specialties/{specialty_id}")
def delete_specialty(specialty_id: int, db: Session = Depends(get_db)):
    """Elimina una specialità."""
    success = user_service.delete_specialty(db, specialty_id=specialty_id)
    if not success:
        raise HTTPException(status_code=404, detail="Specialty not found")
    return {"message": "Specialty deleted successfully"}

# Internal endpoint for Auth service synchronization
@router.post("/users/internal/sync-user", response_model=UserInDB)
def sync_user_from_auth(
    sync_data: dict,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint to synchronize user data from Auth service.
    Creates a user in Users service with the same ID as Auth service.
    """
    user_id = sync_data.get("user_id")
    email = sync_data.get("email")
    name = sync_data.get("name")
    role = sync_data.get("role")
    
    # Check if user already exists
    existing_user = user_service.get_user(db, user_id=user_id)
    if existing_user:
        return existing_user
    
    # Map Auth service roles to Users service user types
    role_mapping = {
        "student": "child",
        "parent": "parent", 
        "professional": "professional",
        "admin": "admin"
    }
    
    user_type = role_mapping.get(role, "child")
    
    # Create user data for Users service
    user_data = UserCreate(
        email=email,
        name=name,
        surname="",  # Will be updated later if needed
        user_type=user_type,
        password="auth_service_managed"  # Placeholder since Auth service manages authentication
    )
    
    # Create user with specific ID from Auth service
    created_user = user_service.create_user_with_id(db, user_data=user_data, user_id=user_id)
    return created_user