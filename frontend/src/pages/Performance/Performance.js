import React from 'react';
import { Zap, Cpu, Database, Activity } from 'lucide-react';

function Performance() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Performance & Métricas</h1>
        <p className="text-gray-600 mt-1">Monitoramento de performance do sistema em tempo real</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">CPU Usage</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">65%</p>
            </div>
            <Cpu className="w-6 h-6 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Memory</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">72%</p>
            </div>
            <Database className="w-6 h-6 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cache Hit Rate</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">89%</p>
            </div>
            <Zap className="w-6 h-6 text-yellow-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Throughput</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">42/min</p>
            </div>
            <Activity className="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Sistema Status</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full" />
              <span className="text-sm font-medium text-gray-700">Redis Cache</span>
            </div>
            <span className="text-sm text-green-600">Healthy</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full" />
              <span className="text-sm font-medium text-gray-700">Parallel Processor</span>
            </div>
            <span className="text-sm text-green-600">Healthy</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-400 rounded-full" />
              <span className="text-sm font-medium text-gray-700">Database Manager</span>
            </div>
            <span className="text-sm text-yellow-600">Degraded</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full" />
              <span className="text-sm font-medium text-gray-700">Metrics Collector</span>
            </div>
            <span className="text-sm text-green-600">Healthy</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Performance; 