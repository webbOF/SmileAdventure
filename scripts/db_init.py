import importlib
import os


def init_all_databases():
    """Inizializza i database creando le tabelle necessarie per Auth, Users e Reports.
       Utilizza gli engine configurati nei rispettivi moduli dei microservizi,
       che leggono DATABASE_URL dalle variabili d'ambiente.
    """
    service_modules_info = {
        "Users": {"session_module": "Users.src.db.session", "model_module": "Users.src.models.user_model"},
        "Auth": {"session_module": "Auth.src.db.session", "model_module": "Auth.src.models.user_model"}, # Assumendo che Auth usi un user_model simile
        "Reports": {"session_module": "Reports.src.db.session", "model_module": "Reports.src.models.report_model"}
    }

    for service_name, paths in service_modules_info.items():
        try:
            print(f"Inizializzazione database per {service_name}...")
            
            session_module_path = paths["session_module"]
            model_module_path = paths["model_module"]

            # Import dinamico dell'engine
            session_module = importlib.import_module(session_module_path)
            engine = getattr(session_module, 'engine')
            
            # Import dinamico di Base
            model_module = importlib.import_module(model_module_path)
            declarative_base = getattr(model_module, 'Base') # Usa un nome diverso per evitare conflitti con 'Base' se è un nome di classe
            
            declarative_base.metadata.create_all(bind=engine)
            print(f"✅ Database per {service_name} inizializzato con successo.")
        except ModuleNotFoundError as e:
            print(f"❌ Errore modulo non trovato per {service_name}: {e}. Controlla PYTHONPATH e i percorsi dei moduli.")
        except AttributeError as e:
            print(f"❌ Errore attributo per {service_name}: {e}. Assicurati che 'engine' e 'Base' siano definiti correttamente nei moduli.")
        except Exception as e:
            print(f"❌ Errore generico nell'inizializzazione del database per {service_name}: {str(e)}")
    
if __name__ == "__main__":
    print(f"Directory di lavoro corrente: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    init_all_databases()
    print("\\nTutti i database specificati sono stati processati per l'inizializzazione.")