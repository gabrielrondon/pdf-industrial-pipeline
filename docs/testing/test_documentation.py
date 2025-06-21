#!/usr/bin/env python3
"""
Test script for the Documentation page functionality
"""

import requests
import time
import sys

def test_documentation_page():
    """Test if the documentation page is accessible and working"""
    
    print("🧪 Testing Documentation Page...")
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Documentation Page Access",
            "url": f"{base_url}/documentation",
            "expected_content": ["PDF Industrial Pipeline", "Documentation"]
        },
        {
            "name": "FastAPI Docs Still Available", 
            "url": f"{base_url}/docs",
            "expected_content": ["swagger-ui", "openapi.json"]
        },
        {
            "name": "Dashboard with Documentation Links",
            "url": f"{base_url}/",
            "expected_content": ["Documentation", "Quick Actions", "API Endpoints"]
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n📋 Testing: {test['name']}")
            response = requests.get(test['url'], timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check if expected content is present
                content_found = all(expected in content for expected in test['expected_content'])
                
                if content_found:
                    print(f"✅ PASS: {test['name']}")
                    results.append(True)
                else:
                    print(f"❌ FAIL: {test['name']} - Expected content not found")
                    print(f"   Expected: {test['expected_content']}")
                    results.append(False)
            else:
                print(f"❌ FAIL: {test['name']} - HTTP {response.status_code}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ FAIL: {test['name']} - Connection error: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 All documentation tests passed! Documentation is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the issues above.")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🔧 PDF Industrial Pipeline - Documentation Test")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    success = test_documentation_page()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ DOCUMENTATION TEST COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ DOCUMENTATION TEST FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 