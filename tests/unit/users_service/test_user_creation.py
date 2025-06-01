#!/usr/bin/env python3

import os
import sys

sys.path.append('.')

# Set the DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"

try:
    from src.db.session import SessionLocal
    from src.models.user_model import UserCreate
    from src.services import user_service
    
    print("Testing user creation...")
    db = SessionLocal()
    
    # Test user creation
    user_data = UserCreate(
        email="test@example.com",
        name="Test",
        surname="User", 
        user_type="child",
        password="testpassword123"
    )
    
    print(f"Creating user: {user_data.email}")
    created_user = user_service.create_user(db, user_data)
    print(f"User created successfully: {created_user.id}")
    
    db.close()
    print("User creation test completed successfully!")
    
except Exception as e:
    print(f"User creation test failed: {e}")
    import traceback
    traceback.print_exc()
