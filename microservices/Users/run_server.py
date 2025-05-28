#!/usr/bin/env python3
"""
Startup script for Users Service
"""
import logging
import os
import sys

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura le variabili d'ambiente se non sono già impostate
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"
    logger.info("DATABASE_URL impostato automaticamente per sviluppo locale")

# Now import and run the app
if __name__ == "__main__":
    try:
        import uvicorn
        from src.main import app
        
        logger.info("Avvio del server Users su porta 8006...")
        uvicorn.run(app, host="0.0.0.0", port=8006, reload=False, log_level="info")
    except Exception as e:
        logger.error(f"Errore nell'avvio del server: {e}")
        sys.exit(1)
