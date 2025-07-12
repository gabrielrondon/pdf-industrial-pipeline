// Main exports
export * from './types';
export * from './services';
export * from './components';
export * from './hooks';

// Question templates
export * from './types/question-templates';

// Re-export commonly used items for convenience
export type {
  FeedbackSystemConfig,
  DocumentType,
  FeedbackType,
  FeedbackQuestion,
  FeedbackSubmission,
  MissingInfoReport,
  CreditReward,
  UserFeedbackStats
} from './types';

export {
  FeedbackProvider,
  useFeedback,
  DocumentFeedback,
  MissingInfoReporter,
  SmartQuickFeedback
} from './components';

export {
  FeedbackService
} from './services';

// Default configuration for easy setup
export const DEFAULT_FEEDBACK_CONFIG = {
  enabled: true,
  apiEndpoint: '/api/v1',
  creditMultipliers: {
    tier_1: 1,
    tier_2: 1.2,
    tier_3: 1.5,
    tier_4: 2
  },
  maxQuestionsPerSession: 8,
  cooldownBetweenSessions: 30,
  peerValidationEnabled: true,
  gamificationEnabled: true
};