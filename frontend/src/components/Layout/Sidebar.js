import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload, 
  Briefcase, 
  BarChart3, 
  Zap, 
  Search, 
  Settings,
  Book,
  ChevronLeft,
  ChevronRight,
  Activity,
  CheckCircle,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';

const Sidebar = () => {
  const location = useLocation();
  const { sidebarCollapsed, setSidebarCollapsed, systemHealth } = useApp();

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/upload', icon: Upload, label: 'Upload' },
    { path: '/jobs', icon: Briefcase, label: 'Jobs' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/performance', icon: Zap, label: 'Performance' },
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/documentation', icon: Book, label: 'Documentation' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'critical':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className={`bg-white shadow-lg transition-all duration-300 ${
      sidebarCollapsed ? 'w-16' : 'w-64'
    } flex flex-col h-full`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-lg font-bold text-gray-900">PDF Pipeline</h1>
              <p className="text-xs text-gray-500">Industrial Processing</p>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4 text-gray-600" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-gray-600" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
              {!sidebarCollapsed && (
                <span className="font-medium">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-gray-200">
        {!sidebarCollapsed ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">System Status</span>
              <Activity className="h-4 w-4 text-gray-400" />
            </div>
            
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
              getStatusColor(systemHealth?.system_status || 'unknown')
            }`}>
              {getStatusIcon(systemHealth?.system_status)}
              <span className="text-sm font-medium capitalize">
                {systemHealth?.system_status || 'Loading...'}
              </span>
            </div>

            {systemHealth && (
              <div className="text-xs text-gray-500 space-y-1">
                <div>Components: {systemHealth.healthy_components}/{systemHealth.total_components}</div>
                <div>Uptime: {Math.floor((systemHealth.uptime_seconds || 0) / 60)}m</div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex justify-center">
            {getStatusIcon(systemHealth?.system_status)}
          </div>
        )}

        {/* Pipeline Stages */}
        {!sidebarCollapsed && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="text-xs font-medium text-gray-700 mb-2">Pipeline Stages</div>
            <div className="space-y-1 text-xs text-gray-600">
              <div className="flex items-center justify-between">
                <span>Stage 1: Ingestion</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 2: OCR</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 3: NLP</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 4: Embeddings</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 5: ML</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 6: Performance</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
              <div className="flex items-center justify-between">
                <span>Stage 7: Frontend</span>
                <CheckCircle className="h-3 w-3 text-green-500" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar; 