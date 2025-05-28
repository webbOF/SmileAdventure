import os
import sys

# Set working directory and add to path
os.chdir(r"c:\Users\arman\Desktop\SeriousGame\microservices\Users")
sys.path.insert(0, os.getcwd())

# Set environment variable
os.environ["DATABASE_URL"] = "postgresql://smile_user:smile_password@localhost:5432/smile_adventure_db"

print("=== USERS SERVICE STARTUP ===")
print(f"Working directory: {os.getcwd()}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

try:
    # Import and run
    import uvicorn
    from src.main import app
    print("✅ Starting Users service on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=False)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
