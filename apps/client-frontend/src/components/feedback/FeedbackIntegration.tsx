import React from 'react';
import {
  FeedbackProvider,
  DocumentFeedback,
  MissingInfoReporter,
  SmartQuickFeedback,
  DocumentType,
  DEFAULT_FEEDBACK_CONFIG
} from '@pdf-pipeline/feedback-system';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

interface FeedbackIntegrationProps {
  documentId: string;
  documentType: DocumentType;
  mlPredictions?: Record<string, any>;
  showQuickFeedback?: boolean;
  showDetailedFeedback?: boolean;
  showMissingInfo?: boolean;
  className?: string;
}

export const FeedbackIntegration: React.FC<FeedbackIntegrationProps> = ({
  documentId,
  documentType,
  mlPredictions,
  showQuickFeedback = true,
  showDetailedFeedback = false,
  showMissingInfo = true,
  className = ''
}) => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  const handleFeedbackComplete = (creditsEarned: number) => {
    toast.success(`🎉 You earned ${creditsEarned} credits! Thank you for your feedback.`);
    
    // Update user credits in UI (trigger context refresh)
    // This would typically update the user's credit balance
    window.dispatchEvent(new CustomEvent('credits-updated', { 
      detail: { earned: creditsEarned } 
    }));
  };

  const handleFeedbackError = (error: string) => {
    toast.error(`Failed to submit feedback: ${error}`);
  };

  const feedbackConfig = {
    ...DEFAULT_FEEDBACK_CONFIG,
    apiEndpoint: '/api/v1', // Use your Railway API endpoint
    creditMultipliers: {
      // Integrate with your existing credit system
      tier_1: user.plan === 'free' ? 1 : 1.2,
      tier_2: user.plan === 'pro' ? 1.5 : 1,
      tier_3: user.plan === 'premium' ? 2 : 1,
      tier_4: 2.5
    }
  };

  return (
    <FeedbackProvider config={feedbackConfig} userId={user.id}>
      <div className={`feedback-integration space-y-4 ${className}`}>
        {/* Quick Feedback for high-confidence predictions */}
        {showQuickFeedback && mlPredictions?.confidence > 0.8 && (
          <SmartQuickFeedback
            documentId={documentId}
            documentType={documentType}
            userId={user.id}
            onComplete={handleFeedbackComplete}
            className="mb-4"
          />
        )}

        {/* Detailed Feedback for uncertain predictions */}
        {showDetailedFeedback && (mlPredictions?.confidence < 0.7 || !mlPredictions) && (
          <DocumentFeedback
            documentId={documentId}
            documentType={documentType}
            userId={user.id}
            mlPredictions={mlPredictions}
            userPlan={user.plan}
            onComplete={handleFeedbackComplete}
            className="mb-4"
          />
        )}

        {/* Missing Information Reporter */}
        {showMissingInfo && (
          <div className="flex justify-end">
            <MissingInfoReporter
              documentId={documentId}
              userId={user.id}
              onSuccess={handleFeedbackComplete}
              className="text-sm"
            />
          </div>
        )}
      </div>
    </FeedbackProvider>
  );
};

// Higher-order component to easily add feedback to existing document components
export const withFeedback = <T extends object>(
  Component: React.ComponentType<T>,
  feedbackOptions: Partial<FeedbackIntegrationProps> = {}
) => {
  const WrappedComponent: React.FC<T & { documentId?: string; documentType?: DocumentType }> = (props) => {
    const { documentId, documentType, ...componentProps } = props;

    return (
      <div className="document-with-feedback">
        <Component {...(componentProps as T)} />
        
        {documentId && documentType && (
          <FeedbackIntegration
            documentId={documentId}
            documentType={documentType}
            {...feedbackOptions}
            className="mt-4 pt-4 border-t border-gray-200"
          />
        )}
      </div>
    );
  };

  WrappedComponent.displayName = `withFeedback(${Component.displayName || Component.name})`;
  return WrappedComponent;
};