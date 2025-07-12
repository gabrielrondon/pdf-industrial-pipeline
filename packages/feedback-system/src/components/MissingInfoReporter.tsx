import React, { useState } from 'react';
import { useFeedback } from './FeedbackProvider';
import { MissingInfoReport, DocumentType } from '../types';

interface MissingInfoReporterProps {
  documentId: string;
  userId: string;
  onSuccess?: (creditsEarned: number) => void;
  onCancel?: () => void;
  className?: string;
}

const CATEGORIES = [
  { value: 'financial', label: 'Financial Information', description: 'Values, debts, taxes, or financial details' },
  { value: 'legal', label: 'Legal Information', description: 'Legal status, compliance, or regulatory details' },
  { value: 'property_details', label: 'Property Details', description: 'Property characteristics, location, or specifications' },
  { value: 'risk_factors', label: 'Risk Factors', description: 'Potential risks or concerns not identified' },
  { value: 'other', label: 'Other', description: 'Any other important information' }
] as const;

const SEVERITY_LEVELS = [
  { value: 'low', label: 'Low', description: 'Nice to have, minor omission' },
  { value: 'medium', label: 'Medium', description: 'Important for decision making' },
  { value: 'high', label: 'High', description: 'Critical information that affects investment' }
] as const;

export const MissingInfoReporter: React.FC<MissingInfoReporterProps> = ({
  documentId,
  userId,
  onSuccess,
  onCancel,
  className = ''
}) => {
  const { state, actions } = useFeedback();
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    category: 'other' as const,
    description: '',
    specificField: '',
    suggestedValue: '',
    severity: 'medium' as const
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting || formData.description.trim().length < 10) return;

    setIsSubmitting(true);

    try {
      const report: MissingInfoReport = {
        documentId,
        category: formData.category,
        description: formData.description.trim(),
        specificField: formData.specificField.trim() || undefined,
        suggestedValue: formData.suggestedValue.trim() || undefined,
        severity: formData.severity,
        userId
      };

      const result = await state.service.reportMissingInfo(report);
      
      if (result.success && result.credits) {
        const creditsEarned = Math.floor(
          result.credits.baseCredits * result.credits.multiplier + result.credits.bonus
        );
        
        // Show success message
        actions.clearError();
        setIsOpen(false);
        resetForm();
        onSuccess?.(creditsEarned);
      }
    } catch (error) {
      console.error('Failed to submit missing info report:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      category: 'other',
      description: '',
      specificField: '',
      suggestedValue: '',
      severity: 'medium'
    });
  };

  const handleCancel = () => {
    setIsOpen(false);
    resetForm();
    actions.clearError();
    onCancel?.();
  };

  if (!state.config.enabled) {
    return null;
  }

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors ${className}`}
      >
        <span className="mr-2">🚩</span>
        Something's Missing?
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">
                  Report Missing Information
                </h2>
                <button
                  onClick={handleCancel}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Help us improve by reporting what the AI missed. Earn up to 15 credits!
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
              {/* Category Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  What type of information is missing?
                </label>
                <div className="space-y-2">
                  {CATEGORIES.map((category) => (
                    <label key={category.value} className="flex items-start">
                      <input
                        type="radio"
                        name="category"
                        value={category.value}
                        checked={formData.category === category.value}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          category: e.target.value as any 
                        }))}
                        className="mt-1 mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{category.label}</div>
                        <div className="text-sm text-gray-600">{category.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe what the AI missed
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    description: e.target.value 
                  }))}
                  placeholder="Example: The document mentions a R$ 50,000 lien that wasn't captured in the analysis..."
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={4}
                  minLength={10}
                  maxLength={500}
                  required
                />
                <div className="text-right text-sm text-gray-500 mt-1">
                  {formData.description.length}/500 characters (minimum 10)
                </div>
              </div>

              {/* Specific Field (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Specific field or section (optional)
                </label>
                <input
                  type="text"
                  value={formData.specificField}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    specificField: e.target.value 
                  }))}
                  placeholder="Example: Property valuation, IPTU amount, Risk assessment..."
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Suggested Value (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Suggested value or correction (optional)
                </label>
                <input
                  type="text"
                  value={formData.suggestedValue}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    suggestedValue: e.target.value 
                  }))}
                  placeholder="Example: R$ 50,000.00, High risk due to environmental issues..."
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Severity Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  How important is this missing information?
                </label>
                <div className="space-y-2">
                  {SEVERITY_LEVELS.map((level) => (
                    <label key={level.value} className="flex items-start">
                      <input
                        type="radio"
                        name="severity"
                        value={level.value}
                        checked={formData.severity === level.value}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          severity: e.target.value as any 
                        }))}
                        className="mt-1 mr-3"
                      />
                      <div>
                        <div className="font-medium text-gray-900">{level.label}</div>
                        <div className="text-sm text-gray-600">{level.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Credit Reward Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex items-center">
                  <span className="text-blue-600 mr-2">💰</span>
                  <div>
                    <div className="font-medium text-blue-900">Credit Rewards</div>
                    <div className="text-sm text-blue-700">
                      Earn 15 base credits for verified reports + quality bonuses
                    </div>
                  </div>
                </div>
              </div>

              {/* Error display */}
              {state.error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-600 text-sm">{state.error}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || formData.description.trim().length < 10}
                  className="px-6 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};