from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.session import engine  # If using SQLAlchemy
from .models import report_model  # If using SQLAlchemy
from .routes import report_routes

report_model.Base.metadata.create_all(bind=engine) # If using SQLAlchemy

app = FastAPI(
    title="SmileAdventure Reports API",
    description="API for managing and generating reports for SmileAdventure.",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_routes.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/status", tags=["System"]) # Changed from /api/v1/reports/status
async def get_status():
    return {"status": "Reports service is running"}

# Root endpoint
@app.get("/", tags=["System"])
async def read_root():
    return {"message": "Welcome to the SmileAdventure Reports API"}
