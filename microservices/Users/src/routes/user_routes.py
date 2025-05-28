from fastapi import APIRouter
from src.controllers.health_records_controller import \
    router as health_records_controller
from src.controllers.user_controller import router as user_controller

router = APIRouter()

# Includiamo il router del controller con il prefisso /api/v1
router.include_router(user_controller, prefix="/api/v1", tags=["Users"])
router.include_router(health_records_controller, prefix="/api/v1/health-records", tags=["Health Records"])