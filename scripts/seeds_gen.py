import importlib
import os


def create_tables_if_not_exist():
    """Creates tables for Auth, Users, and Reports services if they don't already exist,
       using engines configured in their respective microservice modules.
    """
    # SQLite directory creation is no longer needed.
    
    service_modules_info = {
        "Users": {"session_module": "Users.src.db.session", "model_module": "Users.src.models.user_model"},
        "Auth": {"session_module": "Auth.src.db.session", "model_module": "Auth.src.models.user_model"}, 
        "Reports": {"session_module": "Reports.src.db.session", "model_module": "Reports.src.models.report_model"}
    }

    for service_name, paths in service_modules_info.items():
        try:
            print(f"Verifying/Creating tables for {service_name} database...")
            
            session_module_path = paths["session_module"]
            model_module_path = paths["model_module"]

            session_module = importlib.import_module(session_module_path)
            engine = getattr(session_module, 'engine')
            
            model_module = importlib.import_module(model_module_path)
            declarative_base = getattr(model_module, 'Base')
            
            declarative_base.metadata.create_all(bind=engine)
            print(f"✅ Tables for {service_name} verified/created.")
        except ModuleNotFoundError as e:
            print(f"❌ Module not found error for {service_name} in seeds_gen: {e}. Check PYTHONPATH.")
        except AttributeError as e:
            print(f"❌ Attribute error for {service_name} in seeds_gen: {e}. Ensure 'engine' and 'Base' are defined.")
        except Exception as e:
            print(f"❌ Generic error creating tables for {service_name} in seeds_gen: {str(e)}")

# --- SEEDING LOGIC ---
# This section should contain logic to populate tables.
# IMPORTANT: Use SQLAlchemy ORM for data insertion to ensure compatibility 
# with PostgreSQL and other databases. Avoid raw SQLite-specific SQL.

# Example seeding structure (adapt and uncomment as needed):
"""
# from Users.src.db.session import SessionLocal as UsersSessionLocal
# from Users.src.models.user_model import User as UserModel
# # from Auth.src.services.auth_service import get_password_hash # Example if using centralized hashing

# def get_password_hash_placeholder(password: str) -> str:
#     # Replace with actual password hashing logic (e.g., using passlib)
#     import hashlib
#     return hashlib.sha256(password.encode()).hexdigest()

# def seed_users():
#     db_session = UsersSessionLocal()
#     try:
#         if db_session.query(UserModel).count() == 0:
#             print("Populating Users table...")
#             users_data = [
#                 UserModel(email="admin@example.com", username="admin", hashed_password=get_password_hash_placeholder("adminpass"), role="admin", is_active=True),
#                 UserModel(email="professional@example.com", username="doc_brown", hashed_password=get_password_hash_placeholder("profpass"), role="professional", is_active=True, professional_details={"specialization": "Child Psychology", "license_number": "PSY12345"}),
#                 UserModel(email="parent@example.com", username="parent_user", hashed_password=get_password_hash_placeholder("parentpass"), role="parent", is_active=True),
#             ]
#             db_session.add_all(users_data)
#             db_session.commit()
#             print("✅ Users table populated.")
#         else:
#             print("ℹ️ Users table already populated.")
#     except Exception as e:
#         print(f"❌ Error populating Users table: {str(e)}")
#         db_session.rollback()
#     finally:
#         db_session.close()

# Add similar seeding functions for Auth, Reports, etc., if needed.
"""

if __name__ == "__main__":
    print(f"Current working directory (seeds_gen): {os.getcwd()}")
    print(f"PYTHONPATH (seeds_gen): {os.environ.get('PYTHONPATH')}")
    
    print("Starting table creation (if they don't exist) from seeds_gen...")
    create_tables_if_not_exist()
    print("\\nTable creation process (from seeds_gen) completed.")
    
    # print("\\nStarting data seeding...")
    # seed_users() # Uncomment and call necessary seeding functions
    # print("\\nData seeding process completed.")