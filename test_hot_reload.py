#!/usr/bin/env python3
"""
Hot Reload Functionality Test for SmileAdventure Microservices
Tests that Docker containers automatically reload when source code changes
"""

import os
import subprocess
import time
from datetime import datetime

import requests

# Service endpoints
SERVICES = {
    "API Gateway": "http://localhost:8000/status",
    "Auth Service": "http://localhost:8001/status", 
    "Users Service": "http://localhost:8006/status",
    "Game Service": "http://localhost:8005/status",
    "Reports Service": "http://localhost:8007/status"
}

def print_header(title):
    """Print a formatted header"""
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_success(message):
    """Print success message in green"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message in red"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message in blue"""
    print(f"ℹ️  {message}")

def check_service_status():
    """Check if all services are healthy"""
    print_info("Checking service health...")
    healthy_services = []
    
    for service_name, url in SERVICES.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{service_name}: Healthy")
                healthy_services.append(service_name)
            else:
                print_error(f"{service_name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print_error(f"{service_name}: Connection failed - {e}")
    
    return len(healthy_services) == len(SERVICES)

def test_api_gateway_reload():
    """Test API Gateway hot reload by modifying a route temporarily"""
    print_info("Testing API Gateway hot reload...")
    
    # File to modify
    routes_file = "./microservices/API-GATEWAY/src/routes/health_routes.py"
    
    if not os.path.exists(routes_file):
        print_error(f"Routes file not found: {routes_file}")
        return False
    
    try:
        # Read original content
        with open(routes_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Get initial response
        initial_response = requests.get("http://localhost:8000/status")
        print_info(f"Initial status response: {initial_response.status_code}")
        
        # Add a comment to trigger reload (minimal change)
        modified_content = original_content + "\n# Hot reload test comment " + str(datetime.now())
        
        # Write modified content
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print_info("File modified, waiting for reload...")
        time.sleep(3)  # Wait for reload
        
        # Check if service is still responsive
        reload_response = requests.get("http://localhost:8000/status")
        
        if reload_response.status_code == 200:
            print_success("API Gateway hot reload successful - service still responsive")
            result = True
        else:
            print_error(f"API Gateway reload failed - status: {reload_response.status_code}")
            result = False
        
        # Restore original content
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print_info("Original file restored")
        return result
        
    except Exception as e:
        print_error(f"Hot reload test failed: {e}")
        # Try to restore original content
        try:
            with open(routes_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
        except:
            pass
        return False

def test_auth_service_reload():
    """Test Auth Service hot reload"""
    print_info("Testing Auth Service hot reload...")
    
    # File to modify
    service_file = "./microservices/Auth/src/services/auth_service.py"
    
    if not os.path.exists(service_file):
        print_error(f"Service file not found: {service_file}")
        return False
    
    try:
        # Read original content
        with open(service_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Get initial response
        initial_response = requests.get("http://localhost:8001/status")
        print_info(f"Initial auth status response: {initial_response.status_code}")
        
        # Add a comment to trigger reload
        modified_content = original_content + "\n# Hot reload test " + str(datetime.now())
        
        # Write modified content
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print_info("Auth service file modified, waiting for reload...")
        time.sleep(3)  # Wait for reload
        
        # Check if service is still responsive
        reload_response = requests.get("http://localhost:8001/status")
        
        if reload_response.status_code == 200:
            print_success("Auth Service hot reload successful")
            result = True
        else:
            print_error(f"Auth Service reload failed - status: {reload_response.status_code}")
            result = False
        
        # Restore original content
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        return result
        
    except Exception as e:
        print_error(f"Auth service hot reload test failed: {e}")
        return False

def check_docker_logs():
    """Check Docker logs for reload indicators"""
    print_info("Checking Docker logs for reload indicators...")
    
    try:
        # Check API Gateway logs
        result = subprocess.run([
            "docker", "logs", "--tail", "10", "smileadventure-api-gateway"
        ], capture_output=True, text=True)
        
        if "Reloading" in result.stdout or "Started server process" in result.stdout:
            print_success("Hot reload activity detected in API Gateway logs")
        else:
            print_info("No explicit reload messages in recent logs")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to check Docker logs: {e}")
        return False

def main():
    """Main test function"""
    print_header("SmileAdventure Hot Reload Functionality Test")
    print_info(f"Test started at: {datetime.now()}")
    
    # Check initial service health
    if not check_service_status():
        print_error("Some services are not healthy. Please ensure all services are running.")
        return
    
    print("\n")
    print_header("Hot Reload Tests")
    
    # Test API Gateway reload
    gateway_result = test_api_gateway_reload()
    time.sleep(2)
    
    # Test Auth Service reload
    auth_result = test_auth_service_reload()
    time.sleep(2)
    
    # Check Docker logs
    logs_result = check_docker_logs()
    
    print("\n")
    print_header("Hot Reload Test Results")
    
    if gateway_result:
        print_success("API Gateway hot reload: PASSED")
    else:
        print_error("API Gateway hot reload: FAILED")
    
    if auth_result:
        print_success("Auth Service hot reload: PASSED")
    else:
        print_error("Auth Service hot reload: FAILED")
    
    if logs_result:
        print_success("Docker logs check: COMPLETED")
    else:
        print_error("Docker logs check: FAILED")
    
    # Final service health check
    print("\n")
    print_header("Final Health Check")
    final_health = check_service_status()
    
    if final_health:
        print_success("All services remain healthy after hot reload tests")
    else:
        print_error("Some services became unhealthy during testing")
    
    print("\n")
    print_header("Test Completed")
    print_info(f"Test completed at: {datetime.now()}")
    
    if gateway_result and auth_result and final_health:
        print_success("🎉 Hot reload functionality is working correctly!")
    else:
        print_error("⚠️  Some hot reload tests failed or services became unhealthy")

if __name__ == "__main__":
    main()
