import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL del database letto dalla variabile d'ambiente
# Default a una stringa di connessione PostgreSQL locale se non specificata (per sviluppo locale senza Docker)
# La variabile d'ambiente usata nel docker-compose.yml è REPORTS_DATABASE_URL
DATABASE_URL = os.getenv("REPORTS_DATABASE_URL")

if not DATABASE_URL:
    # Set default for local development
    DATABASE_URL = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"
    print(f"⚠️  REPORTS_DATABASE_URL not set, using default: {DATABASE_URL}")

# Creazione del motore di connessione al database
# Rimosso connect_args={"check_same_thread": False} che è specifico per SQLite
engine = create_engine(DATABASE_URL)

# Creazione della sessione del database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creazione della base per la dichiarazione delle tabelle
Base = declarative_base()

# Funzione per ottenere una sessione del database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
