from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.models.user_model import (ChildCreate, ChildInDB, ChildUpdate,
                                   ProfessionalCreate, ProfessionalInDB,
                                   ProfessionalUpdate, SensoryProfileCreate,
                                   SensoryProfileInDB, SensoryProfileUpdate,
                                   SpecialtyCreate, SpecialtyInDB, SpecialtyUpdate,
                                   UserCreate, UserInDB, UserUpdate)
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

# Children endpoints (must be before /users/{user_id} to avoid route conflicts)
@router.post("/users/children", response_model=ChildInDB)
def create_child(child: ChildCreate, db: Session = Depends(get_db)):
    """Create a new child profile."""
    # Verify that the parent exists
    parent = user_service.get_user(db, child.parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent user not found")
    
    return user_service.create_child(db=db, child_data=child)

@router.get("/users/children", response_model=List[ChildInDB])
def read_children(
    skip: int = Query(0), 
    limit: int = Query(100),
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of children. If parent_id is provided, filter by parent."""
    if parent_id:
        return user_service.get_children_by_parent(db, parent_id=parent_id, skip=skip, limit=limit)
    else:
        return user_service.get_children(db, skip=skip, limit=limit)

@router.get("/users/children/my", response_model=List[ChildInDB])
def read_my_children(
    skip: int = Query(0), 
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Get children for the current authenticated user (to be implemented with JWT)."""
    # This will need JWT implementation to get current user ID
    # For now, return empty list or require parent_id parameter
    return []

@router.get("/users/children/{child_id}", response_model=ChildInDB)
def read_child(child_id: int, db: Session = Depends(get_db)):
    """Get a specific child by ID."""
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child

@router.put("/users/children/{child_id}", response_model=ChildInDB)
def update_child(child_id: int, child_update: ChildUpdate, db: Session = Depends(get_db)):
    """Update a child's information."""
    updated_child = user_service.update_child(db, child_id=child_id, child_data=child_update)
    if not updated_child:
        raise HTTPException(status_code=404, detail="Child not found")
    return updated_child

@router.delete("/users/children/{child_id}")
def delete_child(child_id: int, db: Session = Depends(get_db)):
    """Delete a child."""
    success = user_service.delete_child(db, child_id=child_id)
    if not success:
        raise HTTPException(status_code=404, detail="Child not found")
    return {"message": "Child deleted successfully"}

@router.get("/users/children/{child_id}/clinical", response_model=ChildInDB)
def get_child_clinical_view(child_id: int, db: Session = Depends(get_db)):
    """Get clinical view of a child (for professionals)."""
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child

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

# Sensory Profile endpoints
@router.post("/users/sensory-profiles", response_model=SensoryProfileInDB)
def create_sensory_profile(sensory_profile: SensoryProfileCreate, db: Session = Depends(get_db)):
    """Create a new sensory profile for a child."""
    # Verify that the child exists
    child = user_service.get_child(db, sensory_profile.child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Check if child already has a sensory profile
    existing_profile = user_service.get_sensory_profile_by_child(db, sensory_profile.child_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Child already has a sensory profile")
    
    return user_service.create_sensory_profile(db=db, sensory_profile_data=sensory_profile)

@router.get("/users/sensory-profiles", response_model=List[SensoryProfileInDB])
def read_sensory_profiles(
    skip: int = Query(0), 
    limit: int = Query(100),
    child_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of sensory profiles. If child_id is provided, filter by child."""
    if child_id:
        profile = user_service.get_sensory_profile_by_child(db, child_id=child_id)
        return [profile] if profile else []
    else:
        return user_service.get_sensory_profiles(db, skip=skip, limit=limit)

@router.get("/users/sensory-profiles/{profile_id}", response_model=SensoryProfileInDB)
def read_sensory_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a specific sensory profile by ID."""
    profile = user_service.get_sensory_profile(db, sensory_profile_id=profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Sensory profile not found")
    return profile

@router.put("/users/sensory-profiles/{profile_id}", response_model=SensoryProfileInDB)
def update_sensory_profile(profile_id: int, profile_update: SensoryProfileUpdate, db: Session = Depends(get_db)):
    """Update a sensory profile."""
    updated_profile = user_service.update_sensory_profile(db, sensory_profile_id=profile_id, sensory_profile_data=profile_update)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Sensory profile not found")
    return updated_profile

@router.delete("/users/sensory-profiles/{profile_id}")
def delete_sensory_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete a sensory profile."""
    success = user_service.delete_sensory_profile(db, sensory_profile_id=profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sensory profile not found")
    return {"message": "Sensory profile deleted successfully"}

@router.get("/users/children/{child_id}/sensory-profile", response_model=SensoryProfileInDB)
def get_child_sensory_profile(child_id: int, db: Session = Depends(get_db)):
    """Get sensory profile for a specific child."""
    # Verify child exists
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    profile = user_service.get_sensory_profile_by_child(db, child_id=child_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Sensory profile not found for this child")
    return profile