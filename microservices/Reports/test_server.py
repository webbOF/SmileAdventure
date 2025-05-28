#!/usr/bin/env python3
"""
Simple test startup for Reports microservice without database dependency
"""

import sys
from pathlib import Path
import uvicorn

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

print("🎯 STARTING REPORTS MICROSERVICE (TEST MODE)")
print(f"📍 Working directory: {current_dir}")

try:
    # Import FastAPI app without database initialization
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from src.routes import report_routes
    
    app = FastAPI(
        title="SmileAdventure Reports API",
        description="API for managing and generating reports for SmileAdventure.",
        version="0.1.0"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(report_routes.router, prefix="/api/reports")

    # Health check endpoint
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "reports", "mode": "test"}

    print("✅ Reports service started successfully!")
    print("🌐 Running on: http://localhost:8007")
    print("📋 API docs: http://localhost:8007/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8007)

except Exception as e:
    print(f"❌ Failed to start Reports service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
