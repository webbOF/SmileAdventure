import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.session import engine
from src.models.user_model import Base
from src.routes.user_routes import router as user_router

# Inizializzazione dell'app FastAPI
app = FastAPI(
    title="SmileAdventure Users Service",
    description="Servizio di gestione utenti per SmileAdventure",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, limita alle origini specifiche
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrazione del router principale
app.include_router(user_router)

# Creazione delle tabelle nel database
Base.metadata.create_all(bind=engine)

# Endpoint di status check
@app.get("/status")
def status():
    return {"status": "Users service is running"}

# Inizializzazione dei dati di base
@app.on_event("startup")
async def startup_db_client():
    """Inizializza dati di base nel database se necessario."""
    try:
        from src.db.session import SessionLocal
        from src.models.user_model import Specialty, SpecialtyCreate
        from src.services import user_service
        
        db = SessionLocal()
        
        try:
            # Verifica se ci sono già dati nel database
            if db.query(Specialty).count() == 0:
                print("Inizializzazione specialità...")
                # Specialità di base
                specialties = [
                    {"name": "Cardiologia", "description": "Specializzazione in malattie del cuore"},
                    {"name": "Dermatologia", "description": "Specializzazione in malattie della pelle"},
                    {"name": "Ginecologia", "description": "Specializzazione in salute femminile"},
                    {"name": "Psicologia", "description": "Specializzazione in salute mentale"},
                    {"name": "Ortopedia", "description": "Specializzazione in sistema muscolo-scheletrico"},
                    {"name": "Neurologia", "description": "Specializzazione in sistema nervoso"},
                    {"name": "Oculistica", "description": "Specializzazione in vista e occhi"},
                    {"name": "Otorinolaringoiatria", "description": "Specializzazione in orecchie, naso e gola"}
                ]
                
                for specialty in specialties:
                    try:
                        specialty_data = SpecialtyCreate(name=specialty["name"], description=specialty["description"])
                        user_service.create_specialty(db, specialty_data=specialty_data)
                        print(f"Creata specialità: {specialty['name']}")
                    except Exception as e:
                        print(f"Errore creando specialità {specialty['name']}: {e}")
                        # Ignora errori di duplicate key - continua con la prossima specialità
                        continue
                print("Inizializzazione specialità completata")
        finally:
            db.close()
    except Exception as e:
        print(f"Errore durante lo startup: {e}")