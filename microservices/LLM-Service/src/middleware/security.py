import hashlib
import hmac
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for API authentication and validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.bearer = HTTPBearer(auto_error=False)
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key (simple implementation)"""
        # In production, use proper API key validation
        expected_keys = [
            "llm-service-key-2024",  # Static key for testing
            "api-gateway-key",       # For API Gateway
        ]
        return api_key in expected_keys
    
    def validate_jwt_token(self, token: str) -> Optional[dict]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def validate_request_signature(self, request: Request, signature: str) -> bool:
        """Validate request signature for internal service communication"""
        try:
            # Create signature from request data
            timestamp = request.headers.get("X-Timestamp", "")
            body = getattr(request, "_body", b"")
            
            message = f"{request.method}{request.url.path}{timestamp}".encode() + body
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature validation error: {str(e)}")
            return False

async def authenticate_request(
    request: Request,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[HTTPAuthorizationCredentials] = None
):
    """Authenticate incoming requests"""
    
    # Allow health checks without authentication
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return {"type": "public", "user": None}
    
    # Check for API key
    if x_api_key:
        security = SecurityMiddleware("your-secret-key-here")  # From config
        if security.validate_api_key(x_api_key):
            return {"type": "api_key", "user": {"service": "authenticated"}}
    
    # Check for JWT token
    if authorization and authorization.scheme.lower() == "bearer":
        security = SecurityMiddleware("your-secret-key-here")  # From config
        payload = security.validate_jwt_token(authorization.credentials)
        if payload:
            return {"type": "jwt", "user": payload}
    
    # For development, allow requests without authentication
    # In production, uncomment the following lines:
    # raise HTTPException(
    #     status_code=401,
    #     detail="Authentication required",
    #     headers={"WWW-Authenticate": "Bearer"}
    # )
    
    return {"type": "development", "user": None}

def create_jwt_token(payload: dict, secret_key: str, expires_in: int = 3600) -> str:
    """Create JWT token for service-to-service communication"""
    expiration = datetime.utcnow() + timedelta(seconds=expires_in)
    payload.update({"exp": expiration})
    return jwt.encode(payload, secret_key, algorithm="HS256")

async def security_headers_middleware(request: Request, call_next):
    """Add security headers to responses"""
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
