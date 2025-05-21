import os
import sys

from eralchemy2 import render_er

# Crea directory per diagrammi
os.makedirs("docs/diagrams", exist_ok=True)

# Genera un diagramma ER completo (richiede di importare tutti i modelli)
def generate_complete_er():
    from sqlalchemy import MetaData
    from sqlalchemy.ext.declarative import declarative_base

    # Importa tutti i modelli
    sys.path.insert(0, os.path.abspath('.'))
    from Auth.src.models.user_model import Base as AuthBase
    from Catalog.src.models.service_model import Base as CatalogBase
    from Users.src.models.user_model import Base as UsersBase

    # Crea un meta-data combinato
    metadata = MetaData()
    
    # Genera diagrammi separati per ogni servizio
    render_er(AuthBase.metadata, 'docs/diagrams/auth_er.png')
    render_er(UsersBase.metadata, 'docs/diagrams/users_er.png')
    render_er(CatalogBase.metadata, 'docs/diagrams/catalog_er.png')
    
    print("Diagrammi ER generati in docs/diagrams/")

if __name__ == "__main__":
    generate_complete_er()