from fastapi import APIRouter
from src.controllers.user_controller import router as user_controller

router = APIRouter()

# Include only the user controller with /api/v1 prefix
router.include_router(user_controller, prefix="/api/v1", tags=["Users"])