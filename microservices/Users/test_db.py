#!/usr/bin/env python3

import os
import sys

sys.path.append('.')

# Set the DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"

try:
    from src.db.session import SessionLocal
    from src.models.user_model import Specialty, User
    from src.services import user_service
    
    print("Testing database connection...")
    db = SessionLocal()
    
    # Test connection by counting users
    user_count = db.query(User).count()
    print(f"Current user count: {user_count}")
    
    # Test getting specialties
    specialties = db.query(Specialty).all()
    print(f"Specialties count: {len(specialties)}")
    for spec in specialties:
        print(f"  - {spec.name}: {spec.description}")
    
    # Test user service functions
    print("\nTesting user service...")
    users = user_service.get_users(db, skip=0, limit=10)
    print(f"Users from service: {len(users)}")
    
    db.close()
    print("Database test completed successfully!")
    
except Exception as e:
    print(f"Database test failed: {e}")
    import traceback
    traceback.print_exc()
