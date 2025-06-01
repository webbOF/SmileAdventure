import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and tracks service metrics"""
    
    def __init__(self):
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(deque)
        self.error_count = defaultdict(int)
        self.openai_api_calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.analysis_counts = defaultdict(int)
        self.start_time = datetime.now()
        
    def record_request(self, endpoint: str, method: str):
        """Record a request"""
        key = f"{method}:{endpoint}"
        self.request_count[key] += 1
        
    def record_response_time(self, endpoint: str, method: str, duration: float):
        """Record response time"""
        key = f"{method}:{endpoint}"
        self.response_times[key].append(duration)
        
        # Keep only last 1000 measurements
        if len(self.response_times[key]) > 1000:
            self.response_times[key].popleft()
            
    def record_error(self, endpoint: str, method: str, error_type: str):
        """Record an error"""
        key = f"{method}:{endpoint}:{error_type}"
        self.error_count[key] += 1
        
    def record_openai_call(self):
        """Record OpenAI API call"""
        self.openai_api_calls += 1
        
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1
        
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
        
    def record_analysis(self, analysis_type: str):
        """Record analysis performed"""
        self.analysis_counts[analysis_type] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate average response times
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        # Calculate cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "request_counts": dict(self.request_count),
            "average_response_times": avg_response_times,
            "error_counts": dict(self.error_count),
            "openai_api_calls": self.openai_api_calls,
            "cache_metrics": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": cache_hit_rate
            },
            "analysis_counts": dict(self.analysis_counts),
            "timestamp": datetime.now().isoformat()
        }
        
    def reset_metrics(self):
        """Reset all metrics"""
        self.request_count.clear()
        self.response_times.clear()
        self.error_count.clear()
        self.openai_api_calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.analysis_counts.clear()
        self.start_time = datetime.now()

# Global metrics collector
metrics = MetricsCollector()

async def metrics_middleware(request, call_next):
    """Middleware to collect metrics"""
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    # Record request
    metrics.record_request(endpoint, method)
    
    try:
        response = await call_next(request)
        
        # Record response time
        duration = time.time() - start_time
        metrics.record_response_time(endpoint, method, duration)
        
        return response
        
    except Exception as e:
        # Record error
        error_type = type(e).__name__
        metrics.record_error(endpoint, method, error_type)
        duration = time.time() - start_time
        metrics.record_response_time(endpoint, method, duration)
        raise
