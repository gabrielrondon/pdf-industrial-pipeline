import { useState, useEffect, useCallback } from 'react';
import { useFeedback } from '../components/FeedbackProvider';
import {
  FeedbackAnswer,
  FeedbackSubmission,
  FeedbackType,
  DocumentType
} from '../types';

interface UseFeedbackSessionOptions {
  documentId: string;
  documentType: DocumentType;
  userId: string;
  onComplete?: (creditsEarned: number) => void;
  onError?: (error: string) => void;
}

interface UseFeedbackSessionReturn {
  answers: Record<string, FeedbackAnswer>;
  currentQuestionIndex: number;
  isSubmitting: boolean;
  sessionStarted: boolean;
  creditsEarned: number;
  startSession: () => void;
  endSession: () => void;
  updateAnswer: (questionId: string, value: string | number | boolean) => void;
  nextQuestion: () => void;
  previousQuestion: () => void;
  submitFeedback: (feedbackType?: FeedbackType, metadata?: Record<string, any>) => Promise<boolean>;
  resetSession: () => void;
}

export const useFeedbackSession = ({
  documentId,
  documentType,
  userId,
  onComplete,
  onError
}: UseFeedbackSessionOptions): UseFeedbackSessionReturn => {
  const { state, actions } = useFeedback();
  const [answers, setAnswers] = useState<Record<string, FeedbackAnswer>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState<Date>(new Date());

  const creditsEarned = state.currentSession?.creditsEarned || 0;

  const startSession = useCallback(() => {
    actions.startFeedbackSession(documentId, userId);
    setSessionStarted(true);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setQuestionStartTime(new Date());
  }, [documentId, userId, actions]);

  const endSession = useCallback(() => {
    actions.endFeedbackSession();
    setSessionStarted(false);
    setCurrentQuestionIndex(0);
    setAnswers({});
  }, [actions]);

  const updateAnswer = useCallback((questionId: string, value: string | number | boolean) => {
    const timeSpent = Math.floor((new Date().getTime() - questionStartTime.getTime()) / 1000);
    
    const answer: FeedbackAnswer = {
      questionId,
      value,
      timeSpent
    };

    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));

    // Update the session in context
    const updatedAnswers = Object.values({ ...answers, [questionId]: answer });
    actions.updateCurrentSession({
      answers: updatedAnswers,
      currentQuestionIndex
    });

    // Reset timer for next question
    setQuestionStartTime(new Date());
  }, [answers, currentQuestionIndex, questionStartTime, actions]);

  const nextQuestion = useCallback(() => {
    setCurrentQuestionIndex(prev => prev + 1);
    setQuestionStartTime(new Date());
  }, []);

  const previousQuestion = useCallback(() => {
    setCurrentQuestionIndex(prev => Math.max(0, prev - 1));
    setQuestionStartTime(new Date());
  }, []);

  const submitFeedback = useCallback(async (
    feedbackType: FeedbackType = FeedbackType.DETAILED_INPUT,
    metadata: Record<string, any> = {}
  ): Promise<boolean> => {
    if (isSubmitting) return false;

    setIsSubmitting(true);

    try {
      const submission: FeedbackSubmission = {
        documentId,
        documentType,
        feedbackType,
        answers: Object.values(answers),
        userId,
        sessionId: state.currentSession?.sessionId || `session_${Date.now()}`,
        metadata: {
          ...metadata,
          totalTimeSpent: state.currentSession 
            ? Math.floor((new Date().getTime() - state.currentSession.startedAt.getTime()) / 1000)
            : 0,
          questionsAnswered: Object.keys(answers).length,
          finalQuestionIndex: currentQuestionIndex
        }
      };

      const success = await actions.submitFeedback(submission);
      
      if (success) {
        const earnedCredits = state.currentSession?.creditsEarned || 0;
        onComplete?.(earnedCredits);
        return true;
      } else {
        onError?.(state.error || 'Failed to submit feedback');
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Network error';
      onError?.(errorMessage);
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [
    isSubmitting,
    documentId,
    documentType,
    answers,
    userId,
    currentQuestionIndex,
    state.currentSession,
    state.error,
    actions,
    onComplete,
    onError
  ]);

  const resetSession = useCallback(() => {
    setAnswers({});
    setCurrentQuestionIndex(0);
    setIsSubmitting(false);
    setQuestionStartTime(new Date());
    actions.clearError();
  }, [actions]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (sessionStarted) {
        endSession();
      }
    };
  }, [sessionStarted, endSession]);

  return {
    answers,
    currentQuestionIndex,
    isSubmitting,
    sessionStarted,
    creditsEarned,
    startSession,
    endSession,
    updateAnswer,
    nextQuestion,
    previousQuestion,
    submitFeedback,
    resetSession
  };
};