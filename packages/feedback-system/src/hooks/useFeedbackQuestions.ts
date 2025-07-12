import { useState, useEffect } from 'react';
import { useFeedback } from '../components/FeedbackProvider';
import { FeedbackQuestion, DocumentType } from '../types';

interface UseFeedbackQuestionsOptions {
  documentId: string;
  documentType: DocumentType;
  mlPredictions?: Record<string, any>;
  userPlan?: string;
  autoLoad?: boolean;
}

interface UseFeedbackQuestionsReturn {
  questions: FeedbackQuestion[];
  isLoading: boolean;
  error: string | null;
  loadQuestions: () => Promise<void>;
  clearQuestions: () => void;
}

export const useFeedbackQuestions = ({
  documentId,
  documentType,
  mlPredictions,
  userPlan = 'free',
  autoLoad = true
}: UseFeedbackQuestionsOptions): UseFeedbackQuestionsReturn => {
  const { state } = useFeedback();
  const [questions, setQuestions] = useState<FeedbackQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = async () => {
    if (!state.config.enabled) {
      setQuestions([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const fetchedQuestions = await state.service.getFeedbackQuestions(
        documentId,
        documentType,
        mlPredictions,
        userPlan
      );
      setQuestions(fetchedQuestions);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load questions';
      setError(errorMessage);
      setQuestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearQuestions = () => {
    setQuestions([]);
    setError(null);
  };

  // Auto-load on mount or when dependencies change
  useEffect(() => {
    if (autoLoad && documentId && documentType) {
      loadQuestions();
    }
  }, [documentId, documentType, autoLoad, state.config.enabled]);

  return {
    questions,
    isLoading,
    error,
    loadQuestions,
    clearQuestions
  };
};