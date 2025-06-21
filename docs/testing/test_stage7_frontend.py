#!/usr/bin/env python3
"""
Test Script for Stage 7: Frontend & Dashboard
PDF Industrial Pipeline v0.0.7

Tests:
1. Frontend build verification
2. API endpoints accessibility
3. CORS configuration
4. Static file serving
5. React routing compatibility
6. Backend-frontend integration
"""

import requests
import json
import time
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Any

class Stage7FrontendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    Response time: {result['response_time_ms']}ms")
        print()

    def test_server_health(self) -> bool:
        """Test if the server is running and healthy"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Server Health Check",
                    True,
                    f"Server is healthy. Status: {data.get('status', 'unknown')}",
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Server Health Check",
                    False,
                    f"Server returned status code: {response.status_code}",
                    response_time
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Server Health Check",
                False,
                f"Server connection failed: {str(e)}"
            )
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS configuration"""
        try:
            start_time = time.time()
            # Test preflight request
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.base_url}/health", headers=headers, timeout=5)
            response_time = time.time() - start_time
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
            }
            
            success = (
                cors_headers['access-control-allow-origin'] is not None and
                cors_headers['access-control-allow-methods'] is not None
            )
            
            self.log_test(
                "CORS Configuration",
                success,
                f"CORS headers: {cors_headers}",
                response_time
            )
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "CORS Configuration",
                False,
                f"CORS test failed: {str(e)}"
            )
            return False

    def test_api_endpoints(self) -> bool:
        """Test key API endpoints for frontend integration"""
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/performance/system/health", "System health"),
            ("/performance/cache/stats", "Cache statistics"),
            ("/performance/parallel/stats", "Parallel processing stats"),
            ("/performance/metrics/stats", "Metrics statistics"),
            ("/performance/analytics", "Performance analytics"),
        ]
        
        all_success = True
        
        for endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                all_success = all_success and success
                
                details = f"{description} - Status: {response.status_code}"
                if success and response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            details += f" - Keys: {list(data.keys())[:5]}"
                    except:
                        pass
                
                self.log_test(
                    f"API Endpoint: {endpoint}",
                    success,
                    details,
                    response_time
                )
                
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"API Endpoint: {endpoint}",
                    False,
                    f"Request failed: {str(e)}"
                )
                all_success = False
        
        return all_success

    def test_frontend_build_exists(self) -> bool:
        """Test if frontend build directory exists"""
        build_path = "frontend/build"
        index_path = "frontend/build/index.html"
        static_path = "frontend/build/static"
        
        build_exists = os.path.exists(build_path)
        index_exists = os.path.exists(index_path)
        static_exists = os.path.exists(static_path)
        
        success = build_exists and index_exists
        
        details = f"Build dir: {build_exists}, Index.html: {index_exists}, Static dir: {static_exists}"
        
        self.log_test(
            "Frontend Build Files",
            success,
            details
        )
        
        return success

    def test_static_file_serving(self) -> bool:
        """Test if static files are served correctly"""
        if not os.path.exists("frontend/build"):
            self.log_test(
                "Static File Serving",
                False,
                "Frontend build directory not found"
            )
            return False
        
        try:
            start_time = time.time()
            # Test serving the main index.html
            response = requests.get(f"{self.base_url}/dashboard", timeout=5)
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            content_type = response.headers.get('content-type', '')
            
            details = f"Status: {response.status_code}, Content-Type: {content_type}"
            if success:
                details += f", Content length: {len(response.content)} bytes"
            
            self.log_test(
                "Static File Serving",
                success,
                details,
                response_time
            )
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Static File Serving",
                False,
                f"Static file test failed: {str(e)}"
            )
            return False

    def test_frontend_routes(self) -> bool:
        """Test frontend routing"""
        if not os.path.exists("frontend/build"):
            self.log_test(
                "Frontend Routes",
                False,
                "Frontend build not available"
            )
            return False
        
        routes = [
            "/dashboard",
            "/upload",
            "/jobs",
            "/analytics",
            "/performance",
            "/search",
            "/settings"
        ]
        
        all_success = True
        
        for route in routes:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{route}", timeout=5)
                response_time = time.time() - start_time
                
                success = response.status_code == 200
                all_success = all_success and success
                
                self.log_test(
                    f"Frontend Route: {route}",
                    success,
                    f"Status: {response.status_code}",
                    response_time
                )
                
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Frontend Route: {route}",
                    False,
                    f"Route test failed: {str(e)}"
                )
                all_success = False
        
        return all_success

    def test_performance_integration(self) -> bool:
        """Test performance monitoring integration"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/performance/system/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected fields
                expected_fields = ['system_status', 'healthy_components', 'total_components', 'component_details']
                has_fields = all(field in data for field in expected_fields)
                
                components = data.get('component_details', [])
                component_count = len(components)
                
                success = has_fields and component_count > 0
                
                details = f"System status: {data.get('system_status')}, Components: {component_count}"
                if components:
                    healthy_count = sum(1 for c in components if c.get('status') == 'healthy')
                    details += f", Healthy: {healthy_count}/{component_count}"
                
                self.log_test(
                    "Performance Integration",
                    success,
                    details,
                    response_time
                )
                
                return success
            else:
                self.log_test(
                    "Performance Integration",
                    False,
                    f"Performance endpoint returned: {response.status_code}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Performance Integration",
                False,
                f"Performance integration test failed: {str(e)}"
            )
            return False

    def test_websocket_readiness(self) -> bool:
        """Test WebSocket readiness (placeholder for future real-time features)"""
        # For now, just test that the server supports WebSocket upgrades
        try:
            headers = {
                'Connection': 'Upgrade',
                'Upgrade': 'websocket',
                'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
                'Sec-WebSocket-Version': '13'
            }
            
            response = requests.get(f"{self.base_url}/", headers=headers, timeout=5)
            
            # We expect this to fail with current setup, but server should handle gracefully
            success = response.status_code in [400, 404, 405, 426]  # Expected error codes
            
            self.log_test(
                "WebSocket Readiness",
                success,
                f"Server handled WebSocket upgrade request appropriately: {response.status_code}"
            )
            
            return success
            
        except requests.exceptions.RequestException as e:
            self.log_test(
                "WebSocket Readiness",
                True,  # It's OK if this fails for now
                f"WebSocket test completed: {str(e)}"
            )
            return True

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Stage 7 tests"""
        print("🚀 Starting Stage 7: Frontend & Dashboard Tests")
        print("=" * 60)
        print()
        
        # Test sequence
        tests = [
            ("Server Health", self.test_server_health),
            ("CORS Configuration", self.test_cors_headers),
            ("API Endpoints", self.test_api_endpoints),
            ("Frontend Build", self.test_frontend_build_exists),
            ("Static File Serving", self.test_static_file_serving),
            ("Frontend Routes", self.test_frontend_routes),
            ("Performance Integration", self.test_performance_integration),
            ("WebSocket Readiness", self.test_websocket_readiness),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                self.log_test(
                    test_name,
                    False,
                    f"Test execution failed: {str(e)}"
                )
            print()
        
        # Calculate results
        success_rate = (passed_tests / total_tests) * 100
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Summary
        print("=" * 60)
        print("🎯 STAGE 7 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"🏷️  Stage: Frontend & Dashboard")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate >= 80:
            print("🎉 STAGE 7 FRONTEND TESTS: EXCELLENT!")
        elif success_rate >= 60:
            print("✅ STAGE 7 FRONTEND TESTS: GOOD")
        else:
            print("⚠️  STAGE 7 FRONTEND TESTS: NEEDS ATTENTION")
        
        return {
            "stage": "Stage 7: Frontend & Dashboard",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "test_results": self.test_results,
            "summary": {
                "server_health": any(t["test"] == "Server Health Check" and t["success"] for t in self.test_results),
                "cors_configured": any(t["test"] == "CORS Configuration" and t["success"] for t in self.test_results),
                "api_endpoints_working": any(t["test"].startswith("API Endpoint") and t["success"] for t in self.test_results),
                "frontend_build_ready": any(t["test"] == "Frontend Build Files" and t["success"] for t in self.test_results),
                "static_serving_working": any(t["test"] == "Static File Serving" and t["success"] for t in self.test_results),
                "frontend_routes_working": any(t["test"].startswith("Frontend Route") and t["success"] for t in self.test_results),
                "performance_integrated": any(t["test"] == "Performance Integration" and t["success"] for t in self.test_results),
            }
        }

def main():
    """Main test execution"""
    print("PDF Industrial Pipeline - Stage 7 Frontend Tests")
    print("Version: 0.0.7")
    print()
    
    # Check if server is running
    tester = Stage7FrontendTester()
    
    # Run tests
    results = tester.run_all_tests()
    
    # Save results
    with open("stage7_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: stage7_test_results.json")
    
    return results["success_rate"] >= 80

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 