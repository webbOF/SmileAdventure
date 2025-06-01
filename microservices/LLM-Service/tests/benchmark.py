import asyncio
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.llm_models import AnalysisType, GameSessionData, LLMAnalysisRequest


class LLMServiceBenchmark:
    """Performance benchmark for LLM Service"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.results = []
        
    def create_sample_session_data(self, session_id: str = None) -> GameSessionData:
        """Create sample session data for testing"""
        return GameSessionData(
            session_id=session_id or f"benchmark-{int(time.time() * 1000)}",
            child_id=1,
            timestamp=datetime.now(),
            duration_minutes=15,
            game_type="social_interaction",
            activities_completed=["greeting", "eye_contact", "conversation"],
            interaction_events=[
                {
                    "timestamp": datetime.now(),
                    "event_type": "eye_contact_achieved",
                    "duration_seconds": 3.5,
                    "success": True
                },
                {
                    "timestamp": datetime.now(),
                    "event_type": "verbal_response",
                    "response_time_seconds": 2.1,
                    "appropriateness_score": 0.8
                }
            ],
            performance_metrics={
                "social_engagement_score": 0.75,
                "emotional_regulation_score": 0.68,
                "communication_effectiveness": 0.82,
                "task_completion_rate": 0.9
            },
            behavioral_observations=[
                "Child showed improved eye contact during conversation",
                "Demonstrated appropriate emotional responses"
            ],
            emotional_states_detected=[
                {
                    "emotion": "happy",
                    "confidence": 0.85,
                    "duration_seconds": 120
                }
            ]
        )
    
    async def benchmark_endpoint(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        num_requests: int = 10
    ) -> Dict[str, Any]:
        """Benchmark a specific endpoint"""
        print(f"Benchmarking {endpoint} with {num_requests} requests...")
        
        response_times = []
        success_count = 0
        error_count = 0
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_requests):
                start_time = time.time()
                
                try:
                    async with session.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        await response.json()  # Read response
                        
                        duration = time.time() - start_time
                        response_times.append(duration)
                        
                        if response.status == 200:
                            success_count += 1
                        else:
                            error_count += 1
                            
                except Exception as e:
                    duration = time.time() - start_time
                    response_times.append(duration)
                    error_count += 1
                    print(f"Request {i+1} failed: {str(e)}")
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        else:
            avg_time = median_time = min_time = max_time = std_dev = 0
        
        return {
            "endpoint": endpoint,
            "total_requests": num_requests,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": success_count / num_requests,
            "average_response_time": avg_time,
            "median_response_time": median_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "std_deviation": std_dev,
            "requests_per_second": num_requests / sum(response_times) if response_times else 0
        }
    
    async def benchmark_concurrent_requests(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        concurrent_requests: int = 5
    ) -> Dict[str, Any]:
        """Benchmark concurrent requests to an endpoint"""
        print(f"Benchmarking {endpoint} with {concurrent_requests} concurrent requests...")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(concurrent_requests):
                task = session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        success_count = 0
        error_count = 0
        
        for response in responses:
            if isinstance(response, Exception):
                error_count += 1
            elif hasattr(response, 'status') and response.status == 200:
                success_count += 1
            else:
                error_count += 1
        
        return {
            "endpoint": endpoint,
            "concurrent_requests": concurrent_requests,
            "total_time": total_time,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": success_count / concurrent_requests,
            "requests_per_second": concurrent_requests / total_time
        }
    
    async def run_comprehensive_benchmark(self):
        """Run comprehensive benchmark suite"""
        print("Starting LLM Service Performance Benchmark")
        print("=" * 50)
        
        # Test data
        session_data = self.create_sample_session_data()
        analysis_request = LLMAnalysisRequest(
            session_data=session_data,
            analysis_type=AnalysisType.COMPREHENSIVE,
            include_recommendations=True
        )
        
        # Test endpoints
        endpoints_to_test = [
            {
                "endpoint": "/health",
                "data": {},
                "method": "GET"
            },
            {
                "endpoint": "/analyze-emotional-patterns",
                "data": session_data.dict(),
                "method": "POST"
            },
            {
                "endpoint": "/analyze-behavioral-patterns", 
                "data": session_data.dict(),
                "method": "POST"
            },
            {
                "endpoint": "/generate-recommendations",
                "data": session_data.dict(),
                "method": "POST"
            }
        ]
        
        benchmark_results = []
        
        # Sequential benchmarks
        for endpoint_config in endpoints_to_test:
            if endpoint_config["method"] == "POST":
                result = await self.benchmark_endpoint(
                    endpoint_config["endpoint"],
                    endpoint_config["data"],
                    num_requests=10
                )
                benchmark_results.append(result)
                
                # Print results
                print(f"\n{endpoint_config['endpoint']} Results:")
                print(f"  Average Response Time: {result['average_response_time']:.3f}s")
                print(f"  Success Rate: {result['success_rate']:.1%}")
                print(f"  Requests/Second: {result['requests_per_second']:.2f}")
        
        # Concurrent benchmarks
        print("\n" + "=" * 50)
        print("Concurrent Request Benchmarks")
        print("=" * 50)
        
        for endpoint_config in endpoints_to_test:
            if endpoint_config["method"] == "POST":
                concurrent_result = await self.benchmark_concurrent_requests(
                    endpoint_config["endpoint"],
                    endpoint_config["data"],
                    concurrent_requests=5
                )
                
                print(f"\n{endpoint_config['endpoint']} Concurrent Results:")
                print(f"  Total Time: {concurrent_result['total_time']:.3f}s")
                print(f"  Success Rate: {concurrent_result['success_rate']:.1%}")
                print(f"  Requests/Second: {concurrent_result['requests_per_second']:.2f}")
        
        # Memory and resource usage simulation
        print("\n" + "=" * 50)
        print("Resource Usage Test")
        print("=" * 50)
        
        # Test with larger payload
        large_session = self.create_sample_session_data("large-test")
        large_session.behavioral_observations = ["Observation " + str(i) for i in range(100)]
        large_session.interaction_events = [
            {
                "timestamp": datetime.now(),
                "event_type": f"event_{i}",
                "duration_seconds": 1.0,
                "success": True
            }
            for i in range(50)
        ]
        
        large_payload_result = await self.benchmark_endpoint(
            "/analyze-emotional-patterns",
            large_session.dict(),
            num_requests=5
        )
        
        print(f"\nLarge Payload Results:")
        print(f"  Average Response Time: {large_payload_result['average_response_time']:.3f}s")
        print(f"  Success Rate: {large_payload_result['success_rate']:.1%}")
        
        # Save results
        report = {
            "timestamp": datetime.now().isoformat(),
            "sequential_benchmarks": benchmark_results,
            "concurrent_benchmarks": concurrent_result,
            "large_payload_benchmark": large_payload_result,
            "summary": {
                "total_tests": len(benchmark_results),
                "overall_success_rate": statistics.mean([r["success_rate"] for r in benchmark_results]),
                "average_response_time": statistics.mean([r["average_response_time"] for r in benchmark_results])
            }
        }
        
        # Save to file
        with open(f"benchmark_report_{int(time.time())}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n" + "=" * 50)
        print("Benchmark Summary")
        print("=" * 50)
        print(f"Overall Success Rate: {report['summary']['overall_success_rate']:.1%}")
        print(f"Average Response Time: {report['summary']['average_response_time']:.3f}s")
        print(f"Report saved to benchmark_report_{int(time.time())}.json")

async def main():
    """Run the benchmark"""
    benchmark = LLMServiceBenchmark()
    
    # Check if service is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{benchmark.base_url}/health") as response:
                if response.status != 200:
                    print("LLM Service is not running or not healthy")
                    return
    except Exception as e:
        print(f"Cannot connect to LLM Service: {str(e)}")
        print("Please ensure the service is running on http://localhost:8004")
        return
    
    await benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    asyncio.run(main())
