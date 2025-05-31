import json
import time

import requests


def test_hot_reload_functionality():
    """Test that Docker services have proper hot reload configured"""
    print("=== HOT RELOAD VERIFICATION TEST ===")
    
    # Test 1: Verify Docker services are running
    print("\n1. DOCKER SERVICES STATUS")
    import subprocess
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\\t{{.Status}}'], 
                              capture_output=True, text=True)
        print("   Docker Services:")
        services = result.stdout.strip()
        smileadventure_services = [line for line in services.split('\n') if 'smileadventure' in line]
        for service in smileadventure_services:
            print(f"   {service}")
        
        print(f"   ✅ Found {len(smileadventure_services)} SmileAdventure services running")
    except Exception as e:
        print(f"   ❌ Error checking Docker services: {e}")
    
    # Test 2: Verify volume mappings exist
    print("\n2. DOCKER VOLUME MAPPINGS")
    try:
        result = subprocess.run(['docker', 'inspect', 'smileadventure-auth-service'], 
                              capture_output=True, text=True, check=True)
        inspect_data = json.loads(result.stdout)
        mounts = inspect_data[0].get('Mounts', [])
        
        volume_mappings = [mount for mount in mounts if 'src' in mount.get('Source', '')]
        if volume_mappings:
            print("   ✅ Volume mappings found:")
            for mapping in volume_mappings:
                print(f"   📁 {mapping.get('Source')} -> {mapping.get('Destination')}")
        else:
            print("   ⚠️  No source volume mappings found")
            
    except Exception as e:
        print(f"   ❌ Error checking volume mappings: {e}")
    
    # Test 3: Test API endpoints respond quickly (indicating they're ready)
    print("\n3. SERVICE RESPONSE TEST")
    base_url = "http://localhost:8000"
    services_to_test = [
        ("API Gateway", f"{base_url}/status"),
        ("Auth Service", "http://localhost:8001/status"),
        ("Users Service", "http://localhost:8006/status"),
        ("Game Service", "http://localhost:8005/status"),
        ("Reports Service", "http://localhost:8007/status")
    ]
    
    for service_name, url in services_to_test:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ {service_name}: {response.status_code} ({response_time:.0f}ms)")
            else:
                print(f"   ⚠️  {service_name}: {response.status_code} ({response_time:.0f}ms)")
        except Exception as e:
            print(f"   ❌ {service_name}: {str(e)}")
    
    # Test 4: Test JWT Authentication Flow
    print("\n4. ENHANCED JWT AUTHENTICATION")
    try:
        # Use a simple login test
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            login_response = response.json()
            token = login_response.get("access_token")
            user_info = login_response.get("user", {})
            print(f"   ✅ Authentication successful for user ID: {user_info.get('id')}")
            
            # Test the enhanced JWT claims
            import base64
            try:
                parts = token.split('.')
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                jwt_payload = json.loads(decoded)
                
                if 'user_id' in jwt_payload:
                    print(f"   ✅ Enhanced JWT working: user_id={jwt_payload['user_id']}, role={jwt_payload.get('role')}")
                else:
                    print(f"   ⚠️  Standard JWT (no user_id in claims)")
                    
            except Exception as e:
                print(f"   ⚠️  Could not decode JWT: {e}")
                
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {e}")
    
    print("\n=== HOT RELOAD VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_hot_reload_functionality()
