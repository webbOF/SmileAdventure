#!/usr/bin/env python3
"""
Start script for Reports microservice
Handles database URL configuration and service startup
"""

import os
import sys
from pathlib import Path

import uvicorn

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Database URL configuration
if not os.getenv("REPORTS_DATABASE_URL"):
    # Set default database URL for local development
    default_db_url = "postgresql://postgres:password@localhost:5432/smile_adventure_reports"
    os.environ["REPORTS_DATABASE_URL"] = default_db_url
    print(f"🔧 DATABASE_URL set to: {default_db_url}")

print("🎯 STARTING REPORTS MICROSERVICE")
print(f"📍 Working directory: {os.getcwd()}")
print(f"🔗 Database URL: {os.environ.get('REPORTS_DATABASE_URL', 'NOT SET')}")

if __name__ == "__main__":
    try:
        # Import the FastAPI app
        from src.main import app
        
        print("✅ Reports service starting on http://localhost:8007")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8007,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start Reports service: {e}")
        sys.exit(1)
