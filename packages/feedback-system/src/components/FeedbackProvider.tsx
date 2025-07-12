import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { FeedbackService } from '../services/feedback-service';
import {
  FeedbackSystemConfig,
  FeedbackSubmission,
  FeedbackSession,
  UserFeedbackStats,
  CreditReward
} from '../types';

// Default configuration
const DEFAULT_CONFIG: FeedbackSystemConfig = {
  enabled: true,
  apiEndpoint: '/api/v1',
  creditMultipliers: {
    tier_1: 1,
    tier_2: 1.2,
    tier_3: 1.5,
    tier_4: 2
  },
  maxQuestionsPerSession: 8,
  cooldownBetweenSessions: 30, // 30 minutes
  peerValidationEnabled: true,
  gamificationEnabled: true
};

// Context state interface
interface FeedbackState {
  service: FeedbackService;
  config: FeedbackSystemConfig;
  currentSession: FeedbackSession | null;
  userStats: UserFeedbackStats | null;
  isLoading: boolean;
  error: string | null;
  recentCredits: CreditReward | null;
}

// Context actions
type FeedbackAction =
  | { type: 'SET_CONFIG'; payload: Partial<FeedbackSystemConfig> }
  | { type: 'START_SESSION'; payload: FeedbackSession }
  | { type: 'UPDATE_SESSION'; payload: Partial<FeedbackSession> }
  | { type: 'END_SESSION' }
  | { type: 'SET_USER_STATS'; payload: UserFeedbackStats }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_RECENT_CREDITS'; payload: CreditReward | null }
  | { type: 'CLEAR_RECENT_CREDITS' };

// Context interface
interface FeedbackContextType {
  state: FeedbackState;
  actions: {
    updateConfig: (config: Partial<FeedbackSystemConfig>) => void;
    startFeedbackSession: (documentId: string, userId: string) => void;
    updateCurrentSession: (updates: Partial<FeedbackSession>) => void;
    endFeedbackSession: () => void;
    submitFeedback: (submission: FeedbackSubmission) => Promise<boolean>;
    loadUserStats: (userId: string) => Promise<void>;
    clearError: () => void;
    clearRecentCredits: () => void;
    setEnabled: (enabled: boolean) => void;
  };
}

// Reducer function
function feedbackReducer(state: FeedbackState, action: FeedbackAction): FeedbackState {
  switch (action.type) {
    case 'SET_CONFIG':
      const newConfig = { ...state.config, ...action.payload };
      state.service.updateConfig(newConfig);
      return { ...state, config: newConfig };

    case 'START_SESSION':
      return { ...state, currentSession: action.payload, error: null };

    case 'UPDATE_SESSION':
      if (!state.currentSession) return state;
      return {
        ...state,
        currentSession: { ...state.currentSession, ...action.payload }
      };

    case 'END_SESSION':
      return { ...state, currentSession: null };

    case 'SET_USER_STATS':
      return { ...state, userStats: action.payload };

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };

    case 'SET_RECENT_CREDITS':
      return { ...state, recentCredits: action.payload };

    case 'CLEAR_RECENT_CREDITS':
      return { ...state, recentCredits: null };

    default:
      return state;
  }
}

// Create context
const FeedbackContext = createContext<FeedbackContextType | undefined>(undefined);

// Provider props
interface FeedbackProviderProps {
  children: ReactNode;
  config?: Partial<FeedbackSystemConfig>;
  userId?: string;
}

// Provider component
export const FeedbackProvider: React.FC<FeedbackProviderProps> = ({
  children,
  config = {},
  userId
}) => {
  const initialConfig = { ...DEFAULT_CONFIG, ...config };
  const [state, dispatch] = useReducer(feedbackReducer, {
    service: new FeedbackService(initialConfig),
    config: initialConfig,
    currentSession: null,
    userStats: null,
    isLoading: false,
    error: null,
    recentCredits: null
  });

  // Load user stats on mount and when userId changes
  useEffect(() => {
    if (userId && state.config.enabled) {
      loadUserStats(userId);
    }
  }, [userId, state.config.enabled]);

  // Actions
  const updateConfig = (newConfig: Partial<FeedbackSystemConfig>) => {
    dispatch({ type: 'SET_CONFIG', payload: newConfig });
  };

  const startFeedbackSession = (documentId: string, userIdParam: string) => {
    const session: FeedbackSession = {
      sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      documentId,
      userId: userIdParam,
      startedAt: new Date(),
      currentQuestionIndex: 0,
      answers: [],
      timeSpentPerQuestion: [],
      isComplete: false,
      creditsEarned: 0
    };
    
    dispatch({ type: 'START_SESSION', payload: session });
  };

  const updateCurrentSession = (updates: Partial<FeedbackSession>) => {
    dispatch({ type: 'UPDATE_SESSION', payload: updates });
  };

  const endFeedbackSession = () => {
    dispatch({ type: 'END_SESSION' });
  };

  const submitFeedback = async (submission: FeedbackSubmission): Promise<boolean> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const result = await state.service.submitFeedback(submission);
      
      if (result.success && result.credits) {
        dispatch({ type: 'SET_RECENT_CREDITS', payload: result.credits });
        
        // Update session with earned credits
        if (state.currentSession) {
          const totalCredits = result.credits.baseCredits * result.credits.multiplier + result.credits.bonus;
          updateCurrentSession({ 
            creditsEarned: state.currentSession.creditsEarned + totalCredits,
            isComplete: true 
          });
        }

        // Refresh user stats if available
        if (userId) {
          await loadUserStats(userId);
        }
        
        return true;
      } else {
        dispatch({ type: 'SET_ERROR', payload: result.error || 'Failed to submit feedback' });
        return false;
      }
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Network error' 
      });
      return false;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const loadUserStats = async (userIdParam: string) => {
    try {
      const result = await state.service.getUserStats(userIdParam);
      if (result.success && result.data) {
        dispatch({ type: 'SET_USER_STATS', payload: result.data });
      }
    } catch (error) {
      console.warn('Failed to load user feedback stats:', error);
    }
  };

  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null });
  };

  const clearRecentCredits = () => {
    dispatch({ type: 'CLEAR_RECENT_CREDITS' });
  };

  const setEnabled = (enabled: boolean) => {
    updateConfig({ enabled });
  };

  const contextValue: FeedbackContextType = {
    state,
    actions: {
      updateConfig,
      startFeedbackSession,
      updateCurrentSession,
      endFeedbackSession,
      submitFeedback,
      loadUserStats,
      clearError,
      clearRecentCredits,
      setEnabled
    }
  };

  return (
    <FeedbackContext.Provider value={contextValue}>
      {children}
    </FeedbackContext.Provider>
  );
};

// Hook to use feedback context
export const useFeedback = (): FeedbackContextType => {
  const context = useContext(FeedbackContext);
  if (context === undefined) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  return context;
};