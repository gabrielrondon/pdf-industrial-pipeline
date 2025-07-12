import React, { useState, useEffect } from 'react';
import { useFeedback } from './FeedbackProvider';
import {
  DocumentType,
  FeedbackQuestion,
  FeedbackAnswer,
  FeedbackType,
  FeedbackQuestionType,
  FeedbackSubmission
} from '../types';

interface DocumentFeedbackProps {
  documentId: string;
  documentType: DocumentType;
  userId: string;
  mlPredictions?: Record<string, any>;
  userPlan?: string;
  onComplete?: (creditsEarned: number) => void;
  onCancel?: () => void;
  className?: string;
}

export const DocumentFeedback: React.FC<DocumentFeedbackProps> = ({
  documentId,
  documentType,
  userId,
  mlPredictions,
  userPlan = 'free',
  onComplete,
  onCancel,
  className = ''
}) => {
  const { state, actions } = useFeedback();
  const [questions, setQuestions] = useState<FeedbackQuestion[]>([]);
  const [currentAnswers, setCurrentAnswers] = useState<Record<string, FeedbackAnswer>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [startTime, setStartTime] = useState<Date>(new Date());

  // Load questions on mount
  useEffect(() => {
    loadQuestions();
    actions.startFeedbackSession(documentId, userId);
    setStartTime(new Date());
  }, [documentId, documentType]);

  const loadQuestions = async () => {
    try {
      const fetchedQuestions = await state.service.getFeedbackQuestions(
        documentId,
        documentType,
        mlPredictions,
        userPlan
      );
      setQuestions(fetchedQuestions);
    } catch (error) {
      console.error('Failed to load feedback questions:', error);
    }
  };

  const handleAnswerChange = (questionId: string, value: string | number | boolean) => {
    const question = questions.find(q => q.id === questionId);
    if (!question) return;

    const answer: FeedbackAnswer = {
      questionId,
      value,
      timeSpent: Math.floor((new Date().getTime() - startTime.getTime()) / 1000)
    };

    setCurrentAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));

    // Update session
    const answers = Object.values({ ...currentAnswers, [questionId]: answer });
    actions.updateCurrentSession({
      answers,
      currentQuestionIndex: Math.min(currentQuestionIndex + 1, questions.length - 1)
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setStartTime(new Date()); // Reset timer for next question
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setStartTime(new Date());
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);
    
    try {
      const submission: FeedbackSubmission = {
        documentId,
        documentType,
        feedbackType: FeedbackType.DETAILED_INPUT,
        answers: Object.values(currentAnswers),
        userId,
        sessionId: state.currentSession?.sessionId || `session_${Date.now()}`,
        metadata: {
          userPlan,
          mlPredictions,
          totalTimeSpent: Math.floor((new Date().getTime() - (state.currentSession?.startedAt.getTime() || Date.now())) / 1000),
          questionsAnswered: Object.keys(currentAnswers).length,
          totalQuestions: questions.length
        }
      };

      const success = await actions.submitFeedback(submission);
      
      if (success) {
        const creditsEarned = state.currentSession?.creditsEarned || 0;
        actions.endFeedbackSession();
        onComplete?.(creditsEarned);
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    actions.endFeedbackSession();
    onCancel?.();
  };

  // Don't render if feedback is disabled or no questions
  if (!state.config.enabled || questions.length === 0) {
    return null;
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const canProceed = !currentQuestion?.required || currentAnswers[currentQuestion.id];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  return (
    <div className={`feedback-container bg-white border rounded-lg p-6 shadow-sm ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            Help improve our AI
          </h3>
          <button
            onClick={handleCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        <div className="flex justify-between text-sm text-gray-600">
          <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
          <span>+{currentQuestion?.creditReward || 0} credits</span>
        </div>
      </div>

      {/* Current Question */}
      {currentQuestion && (
        <div className="mb-6">
          <QuestionRenderer
            question={currentQuestion}
            value={currentAnswers[currentQuestion.id]?.value}
            onChange={(value) => handleAnswerChange(currentQuestion.id, value)}
          />
          
          {currentQuestion.helpText && (
            <p className="text-sm text-gray-500 mt-2">
              {currentQuestion.helpText}
            </p>
          )}
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        <div className="flex space-x-2">
          {!isLastQuestion ? (
            <button
              onClick={handleNext}
              disabled={!canProceed}
              className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canProceed || isSubmitting}
              className="px-4 py-2 bg-green-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Submitting...' : 'Submit & Earn Credits'}
            </button>
          )}
        </div>
      </div>

      {/* Error display */}
      {state.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600 text-sm">{state.error}</p>
          <button
            onClick={actions.clearError}
            className="text-red-600 underline text-sm mt-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Recent credits earned */}
      {state.recentCredits && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-600 text-sm font-medium">
            🎉 You earned {Math.floor(state.recentCredits.baseCredits * state.recentCredits.multiplier + state.recentCredits.bonus)} credits!
          </p>
          <p className="text-green-600 text-xs mt-1">
            {state.recentCredits.reason}
          </p>
          <button
            onClick={actions.clearRecentCredits}
            className="text-green-600 underline text-xs mt-1"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};

// Question renderer component
interface QuestionRendererProps {
  question: FeedbackQuestion;
  value?: string | number | boolean;
  onChange: (value: string | number | boolean) => void;
}

const QuestionRenderer: React.FC<QuestionRendererProps> = ({
  question,
  value,
  onChange
}) => {
  switch (question.type) {
    case FeedbackQuestionType.YES_NO:
      return (
        <div>
          <p className="font-medium text-gray-900 mb-3">{question.question}</p>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name={question.id}
                value="yes"
                checked={value === true}
                onChange={() => onChange(true)}
                className="mr-2"
              />
              Yes
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name={question.id}
                value="no"
                checked={value === false}
                onChange={() => onChange(false)}
                className="mr-2"
              />
              No
            </label>
          </div>
        </div>
      );

    case FeedbackQuestionType.RATING:
      return (
        <div>
          <p className="font-medium text-gray-900 mb-3">{question.question}</p>
          <div className="flex space-x-2">
            {[1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                onClick={() => onChange(rating)}
                className={`w-10 h-10 rounded-full border-2 ${
                  value === rating
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : 'border-gray-300 text-gray-600 hover:border-blue-300'
                }`}
              >
                {rating}
              </button>
            ))}
          </div>
        </div>
      );

    case FeedbackQuestionType.TEXT_INPUT:
      return (
        <div>
          <label className="block font-medium text-gray-900 mb-2">
            {question.question}
          </label>
          <textarea
            value={value as string || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.placeholder}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
        </div>
      );

    case FeedbackQuestionType.SELECT:
    case FeedbackQuestionType.MULTIPLE_CHOICE:
      return (
        <div>
          <p className="font-medium text-gray-900 mb-3">{question.question}</p>
          <div className="space-y-2">
            {question.options?.map((option, index) => (
              <label key={index} className="flex items-center">
                <input
                  type="radio"
                  name={question.id}
                  value={option}
                  checked={value === option}
                  onChange={() => onChange(option)}
                  className="mr-2"
                />
                {option}
              </label>
            ))}
          </div>
        </div>
      );

    case FeedbackQuestionType.CURRENCY:
      return (
        <div>
          <label className="block font-medium text-gray-900 mb-2">
            {question.question}
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-gray-500">R$</span>
            <input
              type="text"
              value={value as string || ''}
              onChange={(e) => {
                // Format currency input
                const formatted = e.target.value.replace(/[^\d,]/g, '');
                onChange(formatted);
              }}
              placeholder={question.placeholder || '0,00'}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      );

    default:
      return (
        <div>
          <p className="font-medium text-gray-900 mb-2">{question.question}</p>
          <p className="text-gray-500">Unsupported question type</p>
        </div>
      );
  }
};