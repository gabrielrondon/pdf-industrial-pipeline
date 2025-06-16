import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';

// Initial state
const initialState = {
  // System Status
  systemHealth: null,
  isOnline: true,
  lastHealthCheck: null,
  
  // Jobs Management
  jobs: [],
  activeJobs: [],
  completedJobs: [],
  failedJobs: [],
  
  // Performance Metrics
  performanceStats: {
    cache: null,
    parallel: null,
    metrics: null,
    analytics: null,
  },
  
  // UI State
  sidebarOpen: true,
  loading: false,
  currentPage: 'dashboard',
  notifications: [],
  
  // Socket Connection
  socket: null,
  socketConnected: false,
  
  // User Preferences
  theme: 'light',
  language: 'pt-BR',
  autoRefresh: true,
  refreshInterval: 30000, // 30 seconds
};

// Action types
const actionTypes = {
  // System Actions
  SET_SYSTEM_HEALTH: 'SET_SYSTEM_HEALTH',
  SET_ONLINE_STATUS: 'SET_ONLINE_STATUS',
  UPDATE_LAST_HEALTH_CHECK: 'UPDATE_LAST_HEALTH_CHECK',
  
  // Jobs Actions
  SET_JOBS: 'SET_JOBS',
  ADD_JOB: 'ADD_JOB',
  UPDATE_JOB: 'UPDATE_JOB',
  REMOVE_JOB: 'REMOVE_JOB',
  
  // Performance Actions
  SET_PERFORMANCE_STATS: 'SET_PERFORMANCE_STATS',
  UPDATE_CACHE_STATS: 'UPDATE_CACHE_STATS',
  UPDATE_PARALLEL_STATS: 'UPDATE_PARALLEL_STATS',
  UPDATE_METRICS_STATS: 'UPDATE_METRICS_STATS',
  UPDATE_ANALYTICS: 'UPDATE_ANALYTICS',
  
  // UI Actions
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_LOADING: 'SET_LOADING',
  SET_CURRENT_PAGE: 'SET_CURRENT_PAGE',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  CLEAR_NOTIFICATIONS: 'CLEAR_NOTIFICATIONS',
  
  // Socket Actions
  SET_SOCKET: 'SET_SOCKET',
  SET_SOCKET_CONNECTED: 'SET_SOCKET_CONNECTED',
  
  // User Preferences
  SET_THEME: 'SET_THEME',
  SET_LANGUAGE: 'SET_LANGUAGE',
  SET_AUTO_REFRESH: 'SET_AUTO_REFRESH',
  SET_REFRESH_INTERVAL: 'SET_REFRESH_INTERVAL',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_SYSTEM_HEALTH:
      return {
        ...state,
        systemHealth: action.payload,
        lastHealthCheck: new Date().toISOString(),
      };
      
    case actionTypes.SET_ONLINE_STATUS:
      return {
        ...state,
        isOnline: action.payload,
      };
      
    case actionTypes.UPDATE_LAST_HEALTH_CHECK:
      return {
        ...state,
        lastHealthCheck: new Date().toISOString(),
      };
      
    case actionTypes.SET_JOBS:
      return {
        ...state,
        jobs: action.payload,
        activeJobs: action.payload.filter(job => job.status === 'processing' || job.status === 'queued'),
        completedJobs: action.payload.filter(job => job.status === 'completed'),
        failedJobs: action.payload.filter(job => job.status === 'failed'),
      };
      
    case actionTypes.ADD_JOB:
      const newJobs = [...state.jobs, action.payload];
      return {
        ...state,
        jobs: newJobs,
        activeJobs: newJobs.filter(job => job.status === 'processing' || job.status === 'queued'),
        completedJobs: newJobs.filter(job => job.status === 'completed'),
        failedJobs: newJobs.filter(job => job.status === 'failed'),
      };
      
    case actionTypes.UPDATE_JOB:
      const updatedJobs = state.jobs.map(job => 
        job.id === action.payload.id ? { ...job, ...action.payload } : job
      );
      return {
        ...state,
        jobs: updatedJobs,
        activeJobs: updatedJobs.filter(job => job.status === 'processing' || job.status === 'queued'),
        completedJobs: updatedJobs.filter(job => job.status === 'completed'),
        failedJobs: updatedJobs.filter(job => job.status === 'failed'),
      };
      
    case actionTypes.REMOVE_JOB:
      const filteredJobs = state.jobs.filter(job => job.id !== action.payload);
      return {
        ...state,
        jobs: filteredJobs,
        activeJobs: filteredJobs.filter(job => job.status === 'processing' || job.status === 'queued'),
        completedJobs: filteredJobs.filter(job => job.status === 'completed'),
        failedJobs: filteredJobs.filter(job => job.status === 'failed'),
      };
      
    case actionTypes.SET_PERFORMANCE_STATS:
      return {
        ...state,
        performanceStats: {
          ...state.performanceStats,
          ...action.payload,
        },
      };
      
    case actionTypes.UPDATE_CACHE_STATS:
      return {
        ...state,
        performanceStats: {
          ...state.performanceStats,
          cache: action.payload,
        },
      };
      
    case actionTypes.UPDATE_PARALLEL_STATS:
      return {
        ...state,
        performanceStats: {
          ...state.performanceStats,
          parallel: action.payload,
        },
      };
      
    case actionTypes.UPDATE_METRICS_STATS:
      return {
        ...state,
        performanceStats: {
          ...state.performanceStats,
          metrics: action.payload,
        },
      };
      
    case actionTypes.UPDATE_ANALYTICS:
      return {
        ...state,
        performanceStats: {
          ...state.performanceStats,
          analytics: action.payload,
        },
      };
      
    case actionTypes.TOGGLE_SIDEBAR:
      return {
        ...state,
        sidebarOpen: !state.sidebarOpen,
      };
      
    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
      
    case actionTypes.SET_CURRENT_PAGE:
      return {
        ...state,
        currentPage: action.payload,
      };
      
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          ...action.payload,
        }],
      };
      
    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(notification => notification.id !== action.payload),
      };
      
    case actionTypes.CLEAR_NOTIFICATIONS:
      return {
        ...state,
        notifications: [],
      };
      
    case actionTypes.SET_SOCKET:
      return {
        ...state,
        socket: action.payload,
      };
      
    case actionTypes.SET_SOCKET_CONNECTED:
      return {
        ...state,
        socketConnected: action.payload,
      };
      
    case actionTypes.SET_THEME:
      return {
        ...state,
        theme: action.payload,
      };
      
    case actionTypes.SET_LANGUAGE:
      return {
        ...state,
        language: action.payload,
      };
      
    case actionTypes.SET_AUTO_REFRESH:
      return {
        ...state,
        autoRefresh: action.payload,
      };
      
    case actionTypes.SET_REFRESH_INTERVAL:
      return {
        ...state,
        refreshInterval: action.payload,
      };
      
    default:
      return state;
  }
}

// Context
const AppContext = createContext();

// Provider Component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Socket Connection
  useEffect(() => {
    const socket = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socket.on('connect', () => {
      console.log('Socket connected');
      dispatch({ type: actionTypes.SET_SOCKET_CONNECTED, payload: true });
      dispatch({ type: actionTypes.SET_ONLINE_STATUS, payload: true });
      toast.success('Conectado ao servidor');
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
      dispatch({ type: actionTypes.SET_SOCKET_CONNECTED, payload: false });
      dispatch({ type: actionTypes.SET_ONLINE_STATUS, payload: false });
      toast.error('Conexão perdida com o servidor');
    });

    socket.on('job_update', (jobData) => {
      dispatch({ type: actionTypes.UPDATE_JOB, payload: jobData });
      dispatch({
        type: actionTypes.ADD_NOTIFICATION,
        payload: {
          type: 'info',
          title: 'Job Atualizado',
          message: `Job ${jobData.id} - Status: ${jobData.status}`,
        },
      });
    });

    socket.on('job_completed', (jobData) => {
      dispatch({ type: actionTypes.UPDATE_JOB, payload: jobData });
      toast.success(`Job ${jobData.id} concluído com sucesso!`);
    });

    socket.on('job_failed', (jobData) => {
      dispatch({ type: actionTypes.UPDATE_JOB, payload: jobData });
      toast.error(`Job ${jobData.id} falhou: ${jobData.error}`);
    });

    socket.on('system_alert', (alertData) => {
      dispatch({
        type: actionTypes.ADD_NOTIFICATION,
        payload: {
          type: alertData.severity || 'warning',
          title: 'Alerta do Sistema',
          message: alertData.message,
        },
      });
      
      if (alertData.severity === 'error') {
        toast.error(alertData.message);
      } else if (alertData.severity === 'warning') {
        toast(alertData.message, { icon: '⚠️' });
      }
    });

    dispatch({ type: actionTypes.SET_SOCKET, payload: socket });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Health Check
  const checkSystemHealth = useCallback(async () => {
    try {
      const health = await apiService.getSystemHealth();
      dispatch({ type: actionTypes.SET_SYSTEM_HEALTH, payload: health });
      dispatch({ type: actionTypes.SET_ONLINE_STATUS, payload: true });
    } catch (error) {
      console.error('Health check failed:', error);
      dispatch({ type: actionTypes.SET_ONLINE_STATUS, payload: false });
    }
  }, []);

  // Auto Health Check
  useEffect(() => {
    if (state.autoRefresh) {
      const interval = setInterval(checkSystemHealth, state.refreshInterval);
      return () => clearInterval(interval);
    }
  }, [state.autoRefresh, state.refreshInterval, checkSystemHealth]);

  // Initial Health Check
  useEffect(() => {
    checkSystemHealth();
  }, [checkSystemHealth]);

  // Context Value
  const contextValue = {
    state,
    dispatch,
    actionTypes,
    checkSystemHealth,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
} 