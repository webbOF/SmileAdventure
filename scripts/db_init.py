import os
import sys

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath('.'))

def init_all_databases():
    """Inizializza tutti i database creando le tabelle necessarie"""
    # Crea le directory per i database SQLite con percorsi assoluti
    for service in ["Users", "Auth", "Catalog"]:
        data_dir = os.path.join(os.path.abspath('.'), service, "data")
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Directory {data_dir} creata o verificata")
    
    # Users
    try:
        print("Inizializzazione database Users...")
        from Users.src.db.session import engine
        from Users.src.models.user_model import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database Users inizializzato")
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione del database Users: {str(e)}")
    
    # Auth
    try:
        print("Inizializzazione database Auth...")
        from Auth.src.db.session import engine
        from Auth.src.models.user_model import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database Auth inizializzato")
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione del database Auth: {str(e)}")
    
    # Catalog
    try:
        print("Inizializzazione database Catalog...")
        from Catalog.src.db.session import engine
        from Catalog.src.models.service_model import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database Catalog inizializzato")
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione del database Catalog: {str(e)}")
    
if __name__ == "__main__":
    init_all_databases()
    print("\nTutti i database sono stati inizializzati.")