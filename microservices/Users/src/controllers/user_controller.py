from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.constants.error_messages import (CHILD_ALREADY_HAS_SENSORY_PROFILE,
                                          CHILD_DELETED_SUCCESS,
                                          CHILD_NOT_FOUND,
                                          EMAIL_ALREADY_REGISTERED,
                                          PARENT_USER_NOT_FOUND,
                                          SENSORY_PROFILE_DELETED_SUCCESS,
                                          SENSORY_PROFILE_NOT_FOUND,
                                          SENSORY_PROFILE_NOT_FOUND_FOR_CHILD,
                                          SPECIALTY_NOT_FOUND,
                                          USER_DELETED_SUCCESS, USER_NOT_FOUND)
from src.db.session import get_db
from src.models.user_model import (ChildCreate, ChildInDB, ChildUpdate,
                                   ProfessionalCreate, ProfessionalInDB,
                                   SensoryProfileCreate, SensoryProfileInDB,
                                   SensoryProfileUpdate, SpecialtyInDB,
                                   UserCreate, UserInDB, UserUpdate)
from src.services import user_service

router = APIRouter()

# Users endpoints
@router.post("/users/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crea un nuovo utente."""
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=EMAIL_ALREADY_REGISTERED)
    return user_service.create_user(db=db, user_data=user)

@router.post("/professionals/", response_model=ProfessionalInDB)
def create_professional(professional: ProfessionalCreate, db: Session = Depends(get_db)):
    """Crea un nuovo professionista."""
    db_user = user_service.get_user_by_email(db, email=professional.email)
    if db_user:
        raise HTTPException(status_code=400, detail=EMAIL_ALREADY_REGISTERED)
    return user_service.create_professional(db=db, professional_data=professional)

@router.get("/users/", response_model=List[UserInDB])
def read_users(
    skip: int = Query(0), 
    limit: int = Query(100), 
    user_type: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Recupera l'elenco degli utenti o un utente specifico per email."""    # If email is provided, return specific user
    if email:
        db_user = user_service.get_user_by_email(db, email=email)
        if db_user is None:
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
        return [db_user]  # Return as list to match the response model
      # Otherwise return list of users
    users = user_service.get_users(db, skip=skip, limit=limit, user_type=user_type)
    return users

# Children endpoints - Optimized for MVP
@router.post("/children", response_model=ChildInDB)
def create_child(child: ChildCreate, db: Session = Depends(get_db)):
    """Create a new child profile."""
    # Verify that the parent exists
    parent = user_service.get_user(db, child.parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail=PARENT_USER_NOT_FOUND)
    
    return user_service.create_child(db=db, child_data=child)

@router.get("/children", response_model=List[ChildInDB])
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

@router.get("/children/my", response_model=List[ChildInDB])
def read_my_children(
    skip: int = Query(0), 
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Get children for the current authenticated user (to be implemented with JWT)."""
    # This will need JWT implementation to get current user ID
    # For now, return empty list or require parent_id parameter
    return []

@router.get("/children/{child_id}", response_model=ChildInDB)
def read_child(child_id: int, db: Session = Depends(get_db)):
    """Get a specific child by ID."""
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    return child

@router.put("/children/{child_id}", response_model=ChildInDB)
def update_child(child_id: int, child_update: ChildUpdate, db: Session = Depends(get_db)):
    """Update a child's information."""
    updated_child = user_service.update_child(db, child_id=child_id, child_data=child_update)
    if not updated_child:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    return updated_child

@router.delete("/children/{child_id}")
def delete_child(child_id: int, db: Session = Depends(get_db)):
    """Delete a child."""
    success = user_service.delete_child(db, child_id=child_id)
    if not success:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    return {"message": CHILD_DELETED_SUCCESS}

@router.get("/children/{child_id}/clinical", response_model=ChildInDB)
def get_child_clinical_view(child_id: int, db: Session = Depends(get_db)):
    """Get clinical view of a child (for professionals)."""
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    return child

@router.get("/users/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Recupera un utente specifico."""
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
    return db_user

@router.put("/users/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Aggiorna un utente esistente."""
    db_user = user_service.update_user(db, user_id=user_id, user_data=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina un utente."""
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
    return {"message": USER_DELETED_SUCCESS}

# Professionals endpoints - Simplified for MVP
@router.get("/professionals/search", response_model=List[ProfessionalInDB])
def search_professionals(
    specialty_name: Optional[str] = Query(None, description="Filter by specialty name"),
    location_city: Optional[str] = Query(None, description="Filter by city location"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Simple professional search for MVP - search by specialty, location, and minimum rating."""
    professionals = user_service.get_professionals(
        db, 
        skip=skip, 
        limit=limit, 
        specialty_name=specialty_name,
        location_city=location_city,
        min_rating=min_rating
    )
    return professionals

@router.get("/professionals/", response_model=List[ProfessionalInDB])
def read_professionals(
    skip: int = Query(0), 
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Get list of all professionals."""
    professionals = user_service.get_professionals(db, skip=skip, limit=limit)
    return professionals

# Specialties endpoints - Basic read-only for MVP
@router.get("/specialties/", response_model=List[SpecialtyInDB])
def read_specialties(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get list of available specialties."""
    specialties = user_service.get_specialties(db, skip=skip, limit=limit)
    return specialties

@router.get("/specialties/{specialty_id}", response_model=SpecialtyInDB)
def read_specialty(specialty_id: int, db: Session = Depends(get_db)):
    """Get a specific specialty by ID."""
    db_specialty = user_service.get_specialty(db, specialty_id=specialty_id)
    if db_specialty is None:
        raise HTTPException(status_code=404, detail=SPECIALTY_NOT_FOUND)
    return db_specialty

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

# Sensory Profile endpoints - Optimized for MVP
@router.post("/sensory-profiles", response_model=SensoryProfileInDB)
def create_sensory_profile(sensory_profile: SensoryProfileCreate, db: Session = Depends(get_db)):
    """Create a new sensory profile for a child."""
    # Verify that the child exists
    child = user_service.get_child(db, sensory_profile.child_id)
    if not child:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    
    # Check if child already has a sensory profile
    existing_profile = user_service.get_sensory_profile_by_child(db, sensory_profile.child_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail=CHILD_ALREADY_HAS_SENSORY_PROFILE)
    
    return user_service.create_sensory_profile(db=db, sensory_profile_data=sensory_profile)

@router.get("/sensory-profiles", response_model=List[SensoryProfileInDB])
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

@router.get("/sensory-profiles/{profile_id}", response_model=SensoryProfileInDB)
def read_sensory_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a specific sensory profile by ID."""
    profile = user_service.get_sensory_profile(db, sensory_profile_id=profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=SENSORY_PROFILE_NOT_FOUND)
    return profile

@router.put("/sensory-profiles/{profile_id}", response_model=SensoryProfileInDB)
def update_sensory_profile(profile_id: int, profile_update: SensoryProfileUpdate, db: Session = Depends(get_db)):
    """Update a sensory profile."""
    updated_profile = user_service.update_sensory_profile(db, sensory_profile_id=profile_id, sensory_profile_data=profile_update)
    if not updated_profile:
        raise HTTPException(status_code=404, detail=SENSORY_PROFILE_NOT_FOUND)
    return updated_profile

@router.delete("/sensory-profiles/{profile_id}")
def delete_sensory_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete a sensory profile."""
    success = user_service.delete_sensory_profile(db, sensory_profile_id=profile_id)
    if not success:
        raise HTTPException(status_code=404, detail=SENSORY_PROFILE_NOT_FOUND)
    return {"message": SENSORY_PROFILE_DELETED_SUCCESS}

@router.get("/children/{child_id}/sensory-profile", response_model=SensoryProfileInDB)
def get_child_sensory_profile(child_id: int, db: Session = Depends(get_db)):
    """Get sensory profile for a specific child."""
    # Verify child exists
    child = user_service.get_child(db, child_id=child_id)
    if not child:
        raise HTTPException(status_code=404, detail=CHILD_NOT_FOUND)
    
    profile = user_service.get_sensory_profile_by_child(db, child_id=child_id)
    if not profile:
        raise HTTPException(status_code=404, detail=SENSORY_PROFILE_NOT_FOUND_FOR_CHILD)
    return profile