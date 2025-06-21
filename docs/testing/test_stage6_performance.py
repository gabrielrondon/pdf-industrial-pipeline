#!/usr/bin/env python3
"""
Teste Completo - Stage 6: Performance & Scaling

Testa todas as funcionalidades de performance e escalabilidade implementadas
"""

import time
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_stage6_features():
    """Testa funcionalidades Stage 6"""
    print("🚀 Testando Stage 6: Performance & Scaling")
    print("="*60)
    
    session = requests.Session()
    results = {}
    
    # 1. Cache Statistics
    print("\n📊 Testando Cache Statistics...")
    try:
        response = session.get(f"{BASE_URL}/performance/cache/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache Status: {data.get('cache_health', {}).get('status', 'unknown')}")
            results['cache'] = True
        else:
            print(f"❌ Cache falhou: HTTP {response.status_code}")
            results['cache'] = False
    except Exception as e:
        print(f"❌ Cache erro: {e}")
        results['cache'] = False
    
    # 2. Parallel Processing
    print("\n⚡ Testando Processamento Paralelo...")
    try:
        response = session.get(f"{BASE_URL}/performance/parallel/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('parallel_statistics', {})
            print(f"✅ Workers: {stats.get('total_workers', 0)}")
            results['parallel'] = True
        else:
            print(f"❌ Parallel falhou: HTTP {response.status_code}")
            results['parallel'] = False
    except Exception as e:
        print(f"❌ Parallel erro: {e}")
        results['parallel'] = False
    
    # 3. Metrics Collection
    print("\n📈 Testando Coleta de Métricas...")
    try:
        response = session.get(f"{BASE_URL}/performance/metrics/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('metrics_statistics', {})
            print(f"✅ Requests: {stats.get('total_requests', 0)}")
            results['metrics'] = True
        else:
            print(f"❌ Metrics falhou: HTTP {response.status_code}")
            results['metrics'] = False
    except Exception as e:
        print(f"❌ Metrics erro: {e}")
        results['metrics'] = False
    
    # 4. System Health
    print("\n🏥 Testando Health Check...")
    try:
        response = session.get(f"{BASE_URL}/performance/system/health")
        if response.status_code == 200:
            data = response.json()
            status = data.get('system_status', 'unknown')
            components = data.get('total_components', 0)
            print(f"✅ System Status: {status}")
            print(f"✅ Components: {components}")
            results['health'] = True
        else:
            print(f"❌ Health falhou: HTTP {response.status_code}")
            results['health'] = False
    except Exception as e:
        print(f"❌ Health erro: {e}")
        results['health'] = False
    
    # 5. Performance Analytics
    print("\n📊 Testando Analytics...")
    try:
        response = session.get(f"{BASE_URL}/performance/analytics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics gerado em: {data.get('generated_at', 'unknown')}")
            results['analytics'] = True
        else:
            print(f"❌ Analytics falhou: HTTP {response.status_code}")
            results['analytics'] = False
    except Exception as e:
        print(f"❌ Analytics erro: {e}")
        results['analytics'] = False
    
    # 6. Benchmarking
    print("\n🏃 Testando Benchmark...")
    try:
        response = session.get(f"{BASE_URL}/performance/benchmark/health?iterations=10")
        if response.status_code == 200:
            data = response.json()
            result = data.get('benchmark_result', {})
            rating = data.get('performance_rating', 'unknown')
            print(f"✅ Performance Rating: {rating}")
            print(f"✅ Operations/sec: {result.get('operations_per_second', 0):.2f}")
            results['benchmark'] = True
        else:
            print(f"❌ Benchmark falhou: HTTP {response.status_code}")
            results['benchmark'] = False
    except Exception as e:
        print(f"❌ Benchmark erro: {e}")
        results['benchmark'] = False
    
    # Resumo
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES STAGE 6")
    print("="*60)
    
    successful = sum(results.values())
    total = len(results)
    success_rate = (successful / total) * 100
    
    for feature, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {feature.upper()}")
    
    print(f"\n📊 Taxa de Sucesso: {success_rate:.1f}% ({successful}/{total})")
    
    if success_rate >= 80:
        print("\n🎉 STAGE 6 IMPLEMENTADO COM SUCESSO!")
        print("   Sistema de Performance & Scaling operacional")
    elif success_rate >= 60:
        print("\n⚠️ STAGE 6 PARCIALMENTE IMPLEMENTADO")
        print("   Algumas funcionalidades precisam ajustes")
    else:
        print("\n❌ STAGE 6 PRECISA CORREÇÕES")
        print("   Muitos componentes falharam")
    
    print(f"\n🔧 Funcionalidades Stage 6:")
    print(f"   - Cache Inteligente com Redis")
    print(f"   - Processamento Paralelo")
    print(f"   - Coleta de Métricas")
    print(f"   - Monitoramento de Saúde")
    print(f"   - Analytics de Performance")
    print(f"   - Benchmarking de Endpoints")
    
    return {
        'stage': 6,
        'success_rate': success_rate,
        'results': results,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = test_stage6_features()
    
    # Salvar resultado
    with open('test_stage6_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: test_stage6_results.json") 