import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL del database PostgreSQL
# Default a una stringa di connessione PostgreSQL locale se non specificata (per sviluppo locale senza Docker)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Set default for local development - CHANGE THESE CREDENTIALS IN PRODUCTION
    DATABASE_URL = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"
    print(f"⚠️  DATABASE_URL not set, using default: {DATABASE_URL}")

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