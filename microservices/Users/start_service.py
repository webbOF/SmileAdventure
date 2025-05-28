#!/usr/bin/env python3
"""
Users Service Startup Script - SmileAdventure
Handles proper module imports and environment setup
"""
import os
import sys
from pathlib import Path

# Get the Users directory path
USERS_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = USERS_DIR.parent.parent
SRC_DIR = USERS_DIR / "src"

# Add necessary paths to Python path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(USERS_DIR) not in sys.path:
    sys.path.insert(0, str(USERS_DIR))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "postgresql://smile_user:smile_password@localhost:5432/smile_adventure_db")

def main():
    """Start the Users service"""
    try:
        import uvicorn
        from src.main import app
        
        print("🚀 Starting SmileAdventure Users Service...")
        print(f"📁 Working Directory: {USERS_DIR}")
        print(f"🗄️ Database URL: {os.environ.get('DATABASE_URL')}")
        print("🌐 Service will be available at: http://localhost:8006")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8006,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Trying alternative import method...")
        
        # Alternative method - change working directory
        os.chdir(USERS_DIR)
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0", 
            port=8006,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
