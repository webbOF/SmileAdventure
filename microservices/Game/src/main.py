from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import game_routes

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
app.include_router(game_routes.router, prefix="/api/v1/game", tags=["Game"])

@app.get("/status")
async def status():
    return {"status": "online", "service": "game"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the SmileAdventure Game Service"}