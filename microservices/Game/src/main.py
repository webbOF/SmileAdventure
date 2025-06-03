from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import asd_routes, enhanced_routes, game_routes, progress_routes, realtime_ai_routes

# API prefix constant
API_PREFIX = "/api/v1/game"

app = FastAPI(
    title="SmileAdventure Game Service",
    description="Game logic and mechanics service for SmileAdventure",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, limita alle origini specifiche
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include game routes
app.include_router(game_routes.router, prefix=API_PREFIX, tags=["Game"])

# Include ASD-specific routes
app.include_router(asd_routes.router, prefix=API_PREFIX, tags=["ASD Support"])

# Include enhanced routes (combines game + ASD features)
app.include_router(enhanced_routes.router, prefix=API_PREFIX, tags=["Enhanced Game"])

# Include progress tracking routes
app.include_router(progress_routes.router, prefix=API_PREFIX, tags=["Progress Tracking"])

# Include real-time AI integration routes
app.include_router(realtime_ai_routes.router, prefix=API_PREFIX, tags=["Real-time AI"])

@app.get("/status")
async def status():
    return {"status": "online", "service": "game"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SmileAdventure Game Service"}