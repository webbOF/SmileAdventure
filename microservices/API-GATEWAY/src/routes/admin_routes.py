# API Gateway Admin Routes
import os
import time
from datetime import datetime
from typing import Any, Dict

import httpx
import psycopg2
from fastapi import APIRouter, Depends, HTTPException

from ..auth.jwt_auth import get_current_user

router = APIRouter()

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8006")
REPORTS_SERVICE_URL = os.getenv("REPORTS_SERVICE_URL", "http://reports:8007")
GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8008")

# Database connection info
DATABASE_HOST = os.getenv("DATABASE_HOST", "postgres")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "smileadventure_db")
DATABASE_USER = os.getenv("DATABASE_USER", "smileadventure_user")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "smileadventure_password")

@router.get("/system-status", tags=["Admin"])
async def get_system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get comprehensive system status including all services and infrastructure"""
    start_time = time.time()
    
    try:
        # Initialize status structure
        system_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "response_time_ms": 0,
            "services": {},
            "infrastructure": {},
            "performance_metrics": {}
        }
        
        # Check all microservices
        services_to_check = {
            "api_gateway": "http://localhost:8000/status",
            "auth_service": f"{AUTH_SERVICE_URL}/status",
            "users_service": f"{USERS_SERVICE_URL}/status",
            "reports_service": f"{REPORTS_SERVICE_URL}/status",
            "game_service": f"{GAME_SERVICE_URL}/status",
            "llm_service": f"{LLM_SERVICE_URL}/health"
        }
        
        service_issues = 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, url in services_to_check.items():
                service_start = time.time()
                try:
                    response = await client.get(url)
                    service_end = time.time()
                    response_time = round((service_end - service_start) * 1000, 2)
                    
                    if response.status_code == 200:
                        system_status["services"][service_name] = {
                            "status": "healthy",
                            "response_time_ms": response_time,
                            "last_check": datetime.now().isoformat()
                        }
                    else:
                        system_status["services"][service_name] = {
                            "status": "degraded",
                            "response_time_ms": response_time,
                            "status_code": response.status_code,
                            "last_check": datetime.now().isoformat()
                        }
                        service_issues += 1
                except Exception as e:
                    system_status["services"][service_name] = {
                        "status": "offline",
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
                    service_issues += 1
        
        # Check database connectivity
        try:
            conn = psycopg2.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database=DATABASE_NAME,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            system_status["infrastructure"]["database"] = {
                "status": "healthy",
                "type": "PostgreSQL",
                "host": DATABASE_HOST,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            system_status["infrastructure"]["database"] = {
                "status": "offline",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
            service_issues += 1
        
        # Performance metrics
        end_time = time.time()
        total_response_time = round((end_time - start_time) * 1000, 2)
        
        system_status["response_time_ms"] = total_response_time
        system_status["performance_metrics"] = {
            "total_services": len(services_to_check),
            "healthy_services": len(services_to_check) - service_issues,
            "degraded_services": service_issues,
            "uptime_percentage": round(((len(services_to_check) - service_issues) / len(services_to_check)) * 100, 2)
        }
        
        # Determine overall status
        if service_issues == 0:
            system_status["overall_status"] = "healthy"
        elif service_issues < len(services_to_check) / 2:
            system_status["overall_status"] = "degraded"
        else:
            system_status["overall_status"] = "critical"
        
        return system_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/service-health", tags=["Admin"])
async def get_service_health(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed health status of all microservices"""
    try:
        service_health = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Enhanced service checking with detailed metrics
        services_to_check = {
            "auth_service": {
                "url": f"{AUTH_SERVICE_URL}/status",
                "health_url": f"{AUTH_SERVICE_URL}/api/v1/auth/health",
                "description": "Authentication and Authorization Service"
            },
            "users_service": {
                "url": f"{USERS_SERVICE_URL}/status",
                "health_url": f"{USERS_SERVICE_URL}/api/v1/users/health",
                "description": "User Management Service"
            },
            "reports_service": {
                "url": f"{REPORTS_SERVICE_URL}/status",
                "health_url": f"{REPORTS_SERVICE_URL}/api/v1/reports/health",
                "description": "Analytics and Reporting Service"
            },
            "game_service": {
                "url": f"{GAME_SERVICE_URL}/status",
                "health_url": f"{GAME_SERVICE_URL}/api/v1/game/health",
                "description": "Game Logic and Session Management Service"
            },
            "llm_service": {
                "url": f"{LLM_SERVICE_URL}/health",
                "health_url": f"{LLM_SERVICE_URL}/health",
                "description": "AI Analysis and LLM Service"
            }
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, service_info in services_to_check.items():
                service_start = time.time()
                service_data = {
                    "description": service_info["description"],
                    "endpoints": {}
                }
                
                # Check main status endpoint
                try:
                    response = await client.get(service_info["url"])
                    service_end = time.time()
                    response_time = round((service_end - service_start) * 1000, 2)
                    
                    service_data["endpoints"]["status"] = {
                        "url": service_info["url"],
                        "status": "healthy" if response.status_code == 200 else "degraded",
                        "status_code": response.status_code,
                        "response_time_ms": response_time,
                        "response_data": response.json() if response.status_code == 200 else None
                    }
                except Exception as e:
                    service_data["endpoints"]["status"] = {
                        "url": service_info["url"],
                        "status": "offline",
                        "error": str(e)
                    }
                
                # Check health endpoint through API Gateway
                try:
                    health_response = await client.get(f"http://localhost:8000/api/v1/{service_name.replace('_service', '')}/health")
                    service_data["endpoints"]["health"] = {
                        "url": service_info["health_url"],
                        "status": "healthy" if health_response.status_code == 200 else "degraded",
                        "status_code": health_response.status_code,
                        "response_data": health_response.json() if health_response.status_code == 200 else None
                    }
                except Exception as e:
                    service_data["endpoints"]["health"] = {
                        "url": service_info["health_url"],
                        "status": "offline",
                        "error": str(e)
                    }
                
                # Determine overall service status
                status_endpoint_healthy = service_data["endpoints"]["status"]["status"] == "healthy"
                health_endpoint_healthy = service_data["endpoints"]["health"]["status"] == "healthy"
                
                if status_endpoint_healthy and health_endpoint_healthy:
                    service_data["overall_status"] = "healthy"
                elif status_endpoint_healthy or health_endpoint_healthy:
                    service_data["overall_status"] = "degraded"
                else:
                    service_data["overall_status"] = "offline"
                
                service_data["last_check"] = datetime.now().isoformat()
                service_health["services"][service_name] = service_data
        
        return service_health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service health: {str(e)}")

@router.get("/database-status", tags=["Admin"])
async def get_database_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed database connectivity and performance metrics"""
    try:
        database_status = {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "host": DATABASE_HOST,
                "port": DATABASE_PORT,
                "database_name": DATABASE_NAME,
                "user": DATABASE_USER
            },
            "connectivity": {},
            "performance": {},
            "tables": {}
        }
        
        # Test database connectivity
        connection_start = time.time()
        try:
            conn = psycopg2.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database=DATABASE_NAME,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                connect_timeout=10
            )
            connection_end = time.time()
            connection_time = round((connection_end - connection_start) * 1000, 2)
            
            cursor = conn.cursor()
            
            # Basic connectivity test
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            database_status["connectivity"] = {
                "status": "healthy",
                "connection_time_ms": connection_time,
                "last_successful_connection": datetime.now().isoformat()
            }
            
            # Get database version
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()[0]
            database_status["database"]["version"] = version_info
            
            # Performance metrics
            query_start = time.time()
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cursor.fetchone()[0]
            query_end = time.time()
            query_time = round((query_end - query_start) * 1000, 2)
            
            database_status["performance"] = {
                "simple_query_time_ms": query_time,
                "table_count": table_count
            }
            
            # Check specific tables existence
            important_tables = ["users", "children", "game_sessions", "reports"]
            for table_name in important_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    database_status["tables"][table_name] = {
                        "exists": True,
                        "row_count": row_count,
                        "status": "healthy"
                    }
                except Exception as table_error:
                    database_status["tables"][table_name] = {
                        "exists": False,
                        "error": str(table_error),
                        "status": "missing"
                    }
            
            cursor.close()
            conn.close()
            
        except psycopg2.OperationalError as e:
            database_status["connectivity"] = {
                "status": "offline",
                "error": str(e),
                "error_type": "connection_failed",
                "last_attempt": datetime.now().isoformat()
            }
        except Exception as e:
            database_status["connectivity"] = {
                "status": "degraded",
                "error": str(e),
                "error_type": "query_failed",
                "last_attempt": datetime.now().isoformat()
            }
        
        return database_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database status: {str(e)}")
