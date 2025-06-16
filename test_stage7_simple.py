#!/usr/bin/env python3
"""
Simple Test Script for Stage 7: Frontend & Dashboard
"""

import requests
import os
import json
from datetime import datetime

def test_stage7():
    base_url = "http://localhost:8000"
    results = []
    
    print("🚀 Testing Stage 7: Frontend & Dashboard")
    print("=" * 50)
    
    # Test 1: Server Health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        success = response.status_code == 200
        results.append({"test": "Server Health", "success": success})
        print(f"✅ Server Health: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results.append({"test": "Server Health", "success": False})
        print(f"❌ Server Health: FAIL - {e}")
    
    # Test 2: CORS Headers
    try:
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.get(f"{base_url}/health", headers=headers, timeout=5)
        cors_header = response.headers.get('access-control-allow-origin')
        success = cors_header is not None
        results.append({"test": "CORS Headers", "success": success})
        print(f"✅ CORS Headers: {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results.append({"test": "CORS Headers", "success": False})
        print(f"❌ CORS Headers: FAIL - {e}")
    
    # Test 3: API Endpoints
    endpoints = ["/", "/health", "/performance/system/health"]
    api_success = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code != 200:
                api_success = False
        except:
            api_success = False
    
    results.append({"test": "API Endpoints", "success": api_success})
    print(f"✅ API Endpoints: {'PASS' if api_success else 'FAIL'}")
    
    # Test 4: Frontend Build
    build_exists = os.path.exists("frontend/build/index.html")
    results.append({"test": "Frontend Build", "success": build_exists})
    print(f"✅ Frontend Build: {'PASS' if build_exists else 'FAIL'}")
    
    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 Stage 7: EXCELLENT!")
    elif success_rate >= 50:
        print("✅ Stage 7: GOOD")
    else:
        print("⚠️ Stage 7: NEEDS WORK")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = test_stage7()
    exit(0 if success else 1) 