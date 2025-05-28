#!/usr/bin/env python3
"""
Startup script per Users Service - versione robusta
"""
import os
import sys

import uvicorn

# Aggiungi la directory corrente al path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== USERS SERVICE STARTUP ===")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    # Import dell'app FastAPI
    from src.main import app
    print("✅ Successfully imported FastAPI app")
    
    # Verifica della variabile d'ambiente DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"✅ DATABASE_URL configured: {db_url[:50]}...")
    else:
        print("⚠️ DATABASE_URL not set, using default")
    
    # Avvio del server
    print("🚀 Starting Users service on http://0.0.0.0:8006")
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=False)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying to fix import paths...")
    
    # Prova aggiustamento path
    src_dir = os.path.join(current_dir, 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
        try:
            from main import app
            print("✅ Fixed import, starting server...")
            uvicorn.run(app, host="0.0.0.0", port=8006, reload=False)
        except Exception as e2:
            print(f"❌ Still failed: {e2}")
    else:
        print(f"❌ src directory not found at {src_dir}")

except Exception as e:
    print(f"❌ Startup error: {e}")
    sys.exit(1)
