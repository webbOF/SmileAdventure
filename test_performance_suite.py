#!/usr/bin/env python3
"""
WEBBOF Performance and Load Testing Script
Tests system performance under various load conditions
"""

import asyncio
import aiohttp
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_results": [],
            "performance_metrics": {},
            "recommendations": []
        }
        self.auth_token = None
        self.user_id = None

    async def setup_test_user(self, session: aiohttp.ClientSession):
        """Create and authenticate a test user"""
        try:            # Register user
            timestamp = int(time.time())
            register_data = {
                "username": f"perf_test_{timestamp}",
                "name": f"Performance Test User {timestamp}",
                "email": f"perf_test_{timestamp}@example.com",
                "password": "testPassword123!",
                "role": "child"
            }
            
            async with session.post(f"{self.base_url}/auth/register", json=register_data) as response:
                if response.status != 200:
                    logger.error(f"Registration failed: {response.status}")
                    return False
                
                user_data = await response.json()
                logger.info(f"✅ Test user registered: ID {user_data.get('id')}")            # Login user
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            async with session.post(f"{self.base_url}/auth/login", json=login_data) as response:
                if response.status != 200:
                    logger.error(f"Login failed: {response.status}")
                    return False
                
                login_response = await response.json()
                self.auth_token = login_response.get("access_token")
                self.user_id = login_response.get("user_id")
                
                logger.info(f"✅ Test user authenticated: User ID {self.user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ User setup failed: {e}")
            return False

    async def test_endpoint_performance(self, session: aiohttp.ClientSession, 
                                      endpoint: str, method: str = "GET", 
                                      data: Dict = None, requests_count: int = 10):
        """Test individual endpoint performance"""
        response_times = []
        success_count = 0
        
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        logger.info(f"🧪 Testing {method} {endpoint} ({requests_count} requests)")
        
        for i in range(requests_count):
            start_time = time.time()
            
            try:
                if method == "GET":
                    async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                        response_time = (time.time() - start_time) * 1000  # Convert to ms
                        response_times.append(response_time)
                        if response.status < 400:
                            success_count += 1
                            
                elif method == "POST":
                    async with session.post(f"{self.base_url}{endpoint}", 
                                          json=data, headers=headers) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        if response.status < 400:
                            success_count += 1
                            
            except Exception as e:
                logger.warning(f"Request {i+1} failed: {e}")
                response_times.append(10000)  # 10s timeout as failure
        
        # Calculate metrics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        success_rate = (success_count / requests_count) * 100
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "requests_count": requests_count,
            "success_rate": success_rate,
            "avg_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": round(min_response_time, 2),
            "max_response_time_ms": round(max_response_time, 2),
            "status": "PASS" if success_rate >= 90 and avg_response_time < 1000 else "FAIL"
        }
        
        self.results["test_results"].append(result)
        
        logger.info(f"   📊 Avg: {result['avg_response_time_ms']}ms | "
                   f"Success: {result['success_rate']}% | "
                   f"Status: {result['status']}")
        
        return result

    async def test_concurrent_load(self, session: aiohttp.ClientSession, 
                                 endpoint: str, concurrent_requests: int = 20):
        """Test endpoint under concurrent load"""
        logger.info(f"🚀 Testing concurrent load: {concurrent_requests} simultaneous requests to {endpoint}")
        
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        
        async def make_request():
            try:
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    return response.status < 400
            except:
                return False
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r is True)
        success_rate = (success_count / concurrent_requests) * 100
        requests_per_second = concurrent_requests / total_time if total_time > 0 else 0
        
        load_result = {
            "endpoint": endpoint,
            "concurrent_requests": concurrent_requests,
            "total_time_seconds": round(total_time, 2),
            "success_rate": round(success_rate, 2),
            "requests_per_second": round(requests_per_second, 2),
            "status": "PASS" if success_rate >= 80 else "FAIL"
        }
        
        self.results["performance_metrics"]["concurrent_load"] = load_result
        
        logger.info(f"   📊 RPS: {load_result['requests_per_second']} | "
                   f"Success: {load_result['success_rate']}% | "
                   f"Time: {load_result['total_time_seconds']}s")
        
        return load_result

    async def run_full_performance_suite(self):
        """Run comprehensive performance testing"""
        logger.info("🚀 STARTING WEBBOF PERFORMANCE TESTING")
        logger.info("=" * 60)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Setup test user
            if not await self.setup_test_user(session):
                logger.error("❌ Failed to setup test user - aborting performance tests")
                return
            
            # Test individual endpoints
            endpoints_to_test = [
                ("/health", "GET", None),
                ("/auth/status", "GET", None),
                ("/game/health", "GET", None),
                ("/game/scenarios", "GET", None),
                ("/users/health", "GET", None),
                ("/reports/health", "GET", None),
            ]
            
            logger.info("\n📋 Individual Endpoint Performance Testing")
            logger.info("-" * 50)
            
            for endpoint, method, data in endpoints_to_test:
                await self.test_endpoint_performance(session, endpoint, method, data, 20)
                await asyncio.sleep(0.5)  # Brief pause between tests
            
            # Test game session workflow performance
            logger.info("\n🎮 Game Session Workflow Performance")
            logger.info("-" * 50)
            
            game_start_data = {
                "scenario_id": 1,
                "difficulty": "medium"
            }
            
            await self.test_endpoint_performance(session, "/game/start", "POST", game_start_data, 5)
            
            # Concurrent load testing
            logger.info("\n🚀 Concurrent Load Testing")
            logger.info("-" * 50)
            
            await self.test_concurrent_load(session, "/health", 50)
            await self.test_concurrent_load(session, "/game/scenarios", 30)
            await self.test_concurrent_load(session, "/auth/status", 40)
            
            # Calculate overall metrics
            self.calculate_overall_metrics()
            
        # Generate report
        self.generate_performance_report()

    def calculate_overall_metrics(self):
        """Calculate overall system performance metrics"""
        if not self.results["test_results"]:
            return
        
        # Overall response time metrics
        all_avg_times = [r["avg_response_time_ms"] for r in self.results["test_results"]]
        system_avg_response = statistics.mean(all_avg_times)
        
        # Overall success rate
        all_success_rates = [r["success_rate"] for r in self.results["test_results"]]
        system_success_rate = statistics.mean(all_success_rates)
        
        # Count passing tests
        passing_tests = sum(1 for r in self.results["test_results"] if r["status"] == "PASS")
        total_tests = len(self.results["test_results"])
        
        self.results["performance_metrics"]["overall"] = {
            "average_response_time_ms": round(system_avg_response, 2),
            "average_success_rate": round(system_success_rate, 2),
            "passing_tests": passing_tests,
            "total_tests": total_tests,
            "pass_rate": round((passing_tests / total_tests) * 100, 2) if total_tests > 0 else 0
        }
        
        # Generate recommendations
        self.generate_recommendations()

    def generate_recommendations(self):
        """Generate performance recommendations based on results"""
        overall_metrics = self.results["performance_metrics"].get("overall", {})
        avg_response = overall_metrics.get("average_response_time_ms", 0)
        success_rate = overall_metrics.get("average_success_rate", 0)
        
        if avg_response > 500:
            self.results["recommendations"].append(
                "⚠️  High average response time detected. Consider optimizing database queries and adding caching."
            )
        
        if success_rate < 95:
            self.results["recommendations"].append(
                "⚠️  Success rate below 95%. Investigate error handling and service reliability."
            )
        
        # Check concurrent performance
        concurrent_data = self.results["performance_metrics"].get("concurrent_load", {})
        if concurrent_data.get("requests_per_second", 0) < 10:
            self.results["recommendations"].append(
                "⚠️  Low concurrent request handling. Consider implementing connection pooling and load balancing."
            )
        
        if not self.results["recommendations"]:
            self.results["recommendations"].append(
                "✅ Performance metrics are within acceptable ranges for current load."
            )

    def generate_performance_report(self):
        """Generate and save performance test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 PERFORMANCE TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        overall = self.results["performance_metrics"].get("overall", {})
        
        logger.info(f"📈 Overall Performance Metrics:")
        logger.info(f"   • Average Response Time: {overall.get('average_response_time_ms', 0)}ms")
        logger.info(f"   • Average Success Rate: {overall.get('average_success_rate', 0)}%")
        logger.info(f"   • Tests Passed: {overall.get('passing_tests', 0)}/{overall.get('total_tests', 0)}")
        logger.info(f"   • Pass Rate: {overall.get('pass_rate', 0)}%")
        
        # Concurrent load results
        concurrent = self.results["performance_metrics"].get("concurrent_load", {})
        if concurrent:
            logger.info(f"\n🚀 Concurrent Load Performance:")
            logger.info(f"   • Requests per Second: {concurrent.get('requests_per_second', 0)}")
            logger.info(f"   • Concurrent Success Rate: {concurrent.get('success_rate', 0)}%")
        
        # Recommendations
        logger.info(f"\n💡 Recommendations:")
        for rec in self.results["recommendations"]:
            logger.info(f"   {rec}")
        
        # Save detailed report
        report_filename = "webbof_performance_test_report.json"
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\n📄 Detailed report saved to: {report_filename}")
        logger.info("🏁 PERFORMANCE TESTING COMPLETE")

async def main():
    """Main performance testing function"""
    performance_tester = PerformanceTestSuite()
    await performance_tester.run_full_performance_suite()

if __name__ == "__main__":
    asyncio.run(main())
