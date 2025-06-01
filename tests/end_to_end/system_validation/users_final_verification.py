#!/usr/bin/env python3
"""
Final comprehensive Users service verification test
Validates all working functionality and documents current state
"""

import json
import os
import sys

import requests

sys.path.append('.')

# Set the DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://smileadventureuser:smileadventurepass@localhost:5433/smileadventure"

def test_database_connectivity():
    """Test database connection and schema"""
    try:
        import sqlalchemy as sa
        from src.db.session import SessionLocal, engine
        from src.models.user_model import Specialty, User
        
        print("🔍 Testing Database Connectivity...")
        
        db = SessionLocal()
        user_count = db.query(User).count()
        specialty_count = db.query(Specialty).count()
        
        print(f"✅ Database connected successfully")
        print(f"✅ Users in database: {user_count}")
        print(f"✅ Specialties in database: {specialty_count}")
        
        # Verify schema
        inspector = sa.inspect(engine)
        tables = inspector.get_table_names()
        users_columns = len(inspector.get_columns('users')) if 'users' in tables else 0
        
        print(f"✅ Database tables: {tables}")
        print(f"✅ Users table columns: {users_columns}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8006/api/v1"
    results = {}
    
    print("\n🌐 Testing API Endpoints...")
    
    # Test GET endpoints
    get_endpoints = [
        ("/users", "Users listing"),
        ("/specialties", "Specialties listing"),
        ("/professionals/", "Professionals listing"),
    ]
    
    for endpoint, description in get_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ WORKING" if response.status_code == 200 else f"❌ ERROR {response.status_code}"
            results[endpoint] = {
                "status": response.status_code,
                "working": response.status_code == 200,
                "description": description
            }
            print(f"{status}: {description} ({endpoint})")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📊 Returned {len(data)} items")
                
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR",
                "working": False,
                "error": str(e),
                "description": description
            }
            print(f"❌ FAILED: {description} ({endpoint}) - {e}")
    
    # Test POST endpoints
    print("\n📝 Testing POST Endpoints...")
    
    # Test user creation
    user_data = {
        "email": "testapi@example.com",
        "name": "API",
        "surname": "Test",
        "user_type": "parent",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/users/", 
            json=user_data, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        status = "✅ WORKING" if response.status_code in [200, 201] else f"❌ ERROR {response.status_code}"
        results["/users/ POST"] = {
            "status": response.status_code,
            "working": response.status_code in [200, 201],
            "description": "User creation"
        }
        print(f"{status}: User creation (POST /users/)")
        
    except Exception as e:
        results["/users/ POST"] = {
            "status": "ERROR", 
            "working": False,
            "error": str(e),
            "description": "User creation"
        }
        print(f"❌ FAILED: User creation (POST /users/) - {e}")
    
    # Test specialty creation
    specialty_data = {
        "name": "API Test Specialty",
        "description": "Created via API test"
    }
    
    try:
        response = requests.post(
            f"{base_url}/specialties/", 
            json=specialty_data, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        status = "✅ WORKING" if response.status_code in [200, 201] else f"❌ ERROR {response.status_code}"
        results["/specialties/ POST"] = {
            "status": response.status_code,
            "working": response.status_code in [200, 201],
            "description": "Specialty creation"
        }
        print(f"{status}: Specialty creation (POST /specialties/)")
        
    except Exception as e:
        results["/specialties/ POST"] = {
            "status": "ERROR",
            "working": False, 
            "error": str(e),
            "description": "Specialty creation"
        }
        print(f"❌ FAILED: Specialty creation (POST /specialties/) - {e}")
    
    return results

def test_service_layer():
    """Test service layer functionality"""
    try:
        print("\n⚙️ Testing Service Layer...")
        from src.db.session import SessionLocal
        from src.models.user_model import SpecialtyCreate, UserCreate
        from src.services import user_service
        
        db = SessionLocal()
        
        # Test user service
        users = user_service.get_users(db, skip=0, limit=10)
        print(f"✅ User service: Retrieved {len(users)} users")
        
        # Test specialty service
        specialties = user_service.get_specialties(db)
        print(f"✅ Specialty service: Retrieved {len(specialties)} specialties")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Service layer test failed: {e}")
        return False

def generate_summary(db_test, api_results, service_test):
    """Generate final summary"""
    print("\n" + "="*60)
    print("📋 USERS SERVICE VERIFICATION SUMMARY")
    print("="*60)
    
    # Database summary
    db_status = "✅ WORKING" if db_test else "❌ FAILED"
    print(f"Database & Schema: {db_status}")
    
    # Service layer summary  
    service_status = "✅ WORKING" if service_test else "❌ FAILED"
    print(f"Service Layer: {service_status}")
    
    # API summary
    working_endpoints = sum(1 for result in api_results.values() if result.get('working', False))
    total_endpoints = len(api_results)
    api_percentage = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
    
    print(f"API Endpoints: {working_endpoints}/{total_endpoints} working ({api_percentage:.0f}%)")
    
    # Individual endpoint status
    print("\nEndpoint Details:")
    for endpoint, result in api_results.items():
        status = "✅" if result.get('working', False) else "❌"
        print(f"  {status} {endpoint}: {result['description']}")
    
    # Overall functionality estimate
    components = [
        ("Database", 25, db_test),
        ("Service Layer", 25, service_test), 
        ("API Endpoints", 50, api_percentage > 50)
    ]
    
    total_score = sum(weight for name, weight, working in components if working)
    
    print(f"\n🎯 OVERALL FUNCTIONALITY ESTIMATE: {total_score}%")
    
    if total_score >= 75:
        print("✅ Users service is MOSTLY FUNCTIONAL")
    elif total_score >= 50:
        print("⚠️ Users service has PARTIAL FUNCTIONALITY")
    else:
        print("❌ Users service has CRITICAL ISSUES")
    
    print("\nKey Issues:")
    if not db_test:
        print("  - Database connectivity problems")
    if not service_test:
        print("  - Service layer failures")
    if api_percentage < 50:
        print("  - Multiple API endpoint failures")
    if working_endpoints == 0:
        print("  - Complete API failure")
    
    return total_score

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Users Service Verification")
    print("="*60)
    
    # Run all tests
    db_test = test_database_connectivity()
    api_results = test_api_endpoints()  
    service_test = test_service_layer()
    
    # Generate final summary
    final_score = generate_summary(db_test, api_results, service_test)
    
    print(f"\n✅ Verification completed. Final score: {final_score}%")
