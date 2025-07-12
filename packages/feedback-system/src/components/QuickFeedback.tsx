import React, { useState } from 'react';
import { useFeedback } from './FeedbackProvider';
import {
  DocumentType,
  FeedbackSubmission,
  FeedbackType,
  FeedbackAnswer
} from '../types';

interface QuickFeedbackProps {
  documentId: string;
  documentType: DocumentType;
  userId: string;
  question: string;
  creditReward?: number;
  onComplete?: (creditsEarned: number) => void;
  className?: string;
}

export const QuickFeedback: React.FC<QuickFeedbackProps> = ({
  documentId,
  documentType,
  userId,
  question,
  creditReward = 3,
  onComplete,
  className = ''
}) => {
  const { state, actions } = useFeedback();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const handleQuickAnswer = async (answer: boolean) => {
    if (isSubmitting || hasSubmitted) return;

    setIsSubmitting(true);

    try {
      const feedbackAnswer: FeedbackAnswer = {
        questionId: 'quick_feedback',
        value: answer,
        timeSpent: 1 // Quick feedback takes minimal time
      };

      const submission: FeedbackSubmission = {
        documentId,
        documentType,
        feedbackType: FeedbackType.QUICK_QUESTION,
        answers: [feedbackAnswer],
        userId,
        sessionId: `quick_${Date.now()}`,
        metadata: {
          isQuickFeedback: true,
          question
        }
      };

      const success = await actions.submitFeedback(submission);
      
      if (success) {
        setHasSubmitted(true);
        const creditsEarned = state.recentCredits 
          ? Math.floor(state.recentCredits.baseCredits * state.recentCredits.multiplier + state.recentCredits.bonus)
          : creditReward;
        
        onComplete?.(creditsEarned);
        
        // Auto-clear after 3 seconds
        setTimeout(() => {
          actions.clearRecentCredits();
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to submit quick feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!state.config.enabled || hasSubmitted) {
    return null;
  }

  return (
    <div className={`quick-feedback-container bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <span className="text-blue-600 text-lg">💭</span>
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-blue-900 mb-2">
            Quick feedback (+{creditReward} credits)
          </p>
          <p className="text-sm text-blue-800 mb-3">
            {question}
          </p>
          
          <div className="flex space-x-3">
            <button
              onClick={() => handleQuickAnswer(true)}
              disabled={isSubmitting}
              className="inline-flex items-center px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              👍 Yes
            </button>
            
            <button
              onClick={() => handleQuickAnswer(false)}
              disabled={isSubmitting}
              className="inline-flex items-center px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              👎 No
            </button>
          </div>
          
          {isSubmitting && (
            <p className="text-xs text-blue-600 mt-2">Submitting...</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Specialized quick feedback components for common use cases
interface DocumentQuickFeedbackProps {
  documentId: string;
  documentType: DocumentType;
  userId: string;
  onComplete?: (creditsEarned: number) => void;
  className?: string;
}

export const IPTUQuickFeedback: React.FC<DocumentQuickFeedbackProps> = (props) => (
  <QuickFeedback
    {...props}
    question="Did we correctly identify the IPTU information?"
    creditReward={5}
  />
);

export const ValuationQuickFeedback: React.FC<DocumentQuickFeedbackProps> = (props) => (
  <QuickFeedback
    {...props}
    question="Does the property valuation seem reasonable?"
    creditReward={5}
  />
);

export const RiskQuickFeedback: React.FC<DocumentQuickFeedbackProps> = (props) => (
  <QuickFeedback
    {...props}
    question="Is the risk assessment appropriate?"
    creditReward={5}
  />
);

export const AuctionQuickFeedback: React.FC<DocumentQuickFeedbackProps> = (props) => (
  <QuickFeedback
    {...props}
    question="Are the auction details accurate?"
    creditReward={5}
  />
);

// Smart component that automatically selects appropriate quick feedback
export const SmartQuickFeedback: React.FC<DocumentQuickFeedbackProps> = (props) => {
  switch (props.documentType) {
    case DocumentType.IPTU:
      return <IPTUQuickFeedback {...props} />;
    case DocumentType.PROPERTY_VALUATION:
      return <ValuationQuickFeedback {...props} />;
    case DocumentType.RISK_ASSESSMENT:
      return <RiskQuickFeedback {...props} />;
    case DocumentType.JUDICIAL_AUCTION:
      return <AuctionQuickFeedback {...props} />;
    default:
      return (
        <QuickFeedback
          {...props}
          question="Is the AI analysis accurate?"
          creditReward={3}
        />
      );
  }
};