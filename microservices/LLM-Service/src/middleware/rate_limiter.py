import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = defaultdict(list)
        
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_reset_time(self, client_id: str) -> Optional[int]:
        """Get time until rate limit resets"""
        if not self.requests[client_id]:
            return None
        
        oldest_request = min(self.requests[client_id])
        reset_time = oldest_request + timedelta(seconds=self.time_window)
        return int((reset_time - datetime.now()).total_seconds())

# Global rate limiter instances
request_limiter = RateLimiter(max_requests=60, time_window=60)  # 60 requests per minute
analysis_limiter = RateLimiter(max_requests=20, time_window=60)  # 20 analysis requests per minute

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    # Choose appropriate limiter based on endpoint
    if request.url.path.startswith("/analyze"):
        limiter = analysis_limiter
        limit_type = "analysis"
    else:
        limiter = request_limiter
        limit_type = "general"
    
    if not limiter.is_allowed(client_ip):
        reset_time = limiter.get_reset_time(client_ip)
        logger.warning(f"Rate limit exceeded for {client_ip} on {limit_type} endpoints")
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Too many {limit_type} requests",
                "retry_after": reset_time
            },
            headers={"Retry-After": str(reset_time)} if reset_time else {}
        )
    
    response = await call_next(request)
    return response
