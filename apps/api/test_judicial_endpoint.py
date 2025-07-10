"""
Test script to verify the judicial analysis endpoint
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("=== Testing Judicial Analysis Endpoints ===\n")
    
    # Test job_id (você precisa substituir por um job_id válido)
    job_id = "98ac5938-b0b8-4fc3-8546-18b65ac20115"
    
    print(f"Testing with job_id: {job_id}\n")
    
    # Test POST endpoint
    print("1. Testing POST /judicial-analysis/{job_id}")
    try:
        response = requests.post(f"{BASE_URL}/judicial-analysis/{job_id}")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ POST endpoint working!")
            print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n2. Testing GET /judicial-analysis/{job_id}")
    try:
        response = requests.get(f"{BASE_URL}/judicial-analysis/{job_id}")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ GET endpoint working!")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test API documentation
    print("\n3. Checking API documentation")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API docs available at http://localhost:8000/docs")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

if __name__ == "__main__":
    test_endpoints()
    print("\n💡 Dica: Se o servidor não estiver rodando, execute:")
    print("   python main.py")
    print("\n💡 Para testar com um job válido:")
    print("   1. Faça upload de um PDF")
    print("   2. Execute a análise de texto")
    print("   3. Use o job_id retornado")