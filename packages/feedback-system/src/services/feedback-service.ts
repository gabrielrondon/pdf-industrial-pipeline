import {
  FeedbackSubmission,
  FeedbackApiResponse,
  DocumentFeedbackContext,
  FeedbackQuestion,
  MissingInfoReport,
  CreditReward,
  UserFeedbackStats,
  FeedbackSystemConfig,
  DocumentType
} from '../types';
import { DOCUMENT_QUESTION_TEMPLATES, QUICK_VALIDATION_QUESTIONS } from '../types/question-templates';

export class FeedbackService {
  private config: FeedbackSystemConfig;
  private apiEndpoint: string;

  constructor(config: FeedbackSystemConfig) {
    this.config = config;
    this.apiEndpoint = config.apiEndpoint;
  }

  /**
   * Get appropriate feedback questions for a document
   */
  async getFeedbackQuestions(
    documentId: string,
    documentType: DocumentType,
    mlPredictions?: Record<string, any>,
    userPlan?: string
  ): Promise<FeedbackQuestion[]> {
    if (!this.config.enabled) {
      return [];
    }

    try {
      // First try to get questions from API (for dynamic generation)
      const response = await fetch(`${this.apiEndpoint}/feedback/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          documentId,
          documentType,
          mlPredictions,
          userPlan
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.questions || this.getStaticQuestions(documentType, mlPredictions);
      }
    } catch (error) {
      console.warn('Failed to fetch dynamic questions, using static templates:', error);
    }

    // Fallback to static questions
    return this.getStaticQuestions(documentType, mlPredictions);
  }

  /**
   * Get static questions from templates based on document type and confidence
   */
  private getStaticQuestions(
    documentType: DocumentType,
    mlPredictions?: Record<string, any>
  ): FeedbackQuestion[] {
    const template = DOCUMENT_QUESTION_TEMPLATES.find(t => t.documentType === documentType);
    
    if (!template) {
      return [];
    }

    // Check if we should use quick questions (high confidence) or detailed questions
    const confidence = mlPredictions?.confidence || 0;
    const threshold = template.triggerConditions?.confidenceThreshold || 0.7;

    if (confidence > threshold && this.config.enabled) {
      // High confidence: use quick validation questions
      return QUICK_VALIDATION_QUESTIONS[documentType] || [];
    }

    // Low confidence or no prediction: use detailed questions
    const questions = template.questions;
    
    // Apply user plan restrictions if configured
    if (mlPredictions?.userPlan === 'free') {
      // Free users get fewer questions
      return questions.slice(0, Math.min(3, questions.length));
    }

    return questions.slice(0, this.config.maxQuestionsPerSession);
  }

  /**
   * Submit user feedback
   */
  async submitFeedback(submission: FeedbackSubmission): Promise<FeedbackApiResponse<CreditReward>> {
    if (!this.config.enabled) {
      return { success: false, error: 'Feedback system is disabled' };
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/feedback/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submission)
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { success: false, error: data.error || 'Failed to submit feedback' };
      }

      return {
        success: true,
        data: data.credits,
        credits: data.credits
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Report missing information
   */
  async reportMissingInfo(report: MissingInfoReport): Promise<FeedbackApiResponse<CreditReward>> {
    if (!this.config.enabled) {
      return { success: false, error: 'Feedback system is disabled' };
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/feedback/missing-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { success: false, error: data.error || 'Failed to report missing information' };
      }

      return {
        success: true,
        data: data.credits,
        credits: data.credits
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Get user feedback statistics
   */
  async getUserStats(userId: string): Promise<FeedbackApiResponse<UserFeedbackStats>> {
    if (!this.config.enabled) {
      return { success: false, error: 'Feedback system is disabled' };
    }

    try {
      const response = await fetch(`${this.apiEndpoint}/feedback/user-stats/${userId}`);
      const data = await response.json();
      
      if (!response.ok) {
        return { success: false, error: data.error || 'Failed to fetch user stats' };
      }

      return { success: true, data: data.stats };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Calculate credit rewards with multipliers
   */
  calculateCredits(
    baseCredits: number,
    userStats?: UserFeedbackStats,
    qualityScore?: number
  ): CreditReward {
    let multiplier = 1;
    let bonus = 0;

    if (userStats) {
      // Streak bonus
      if (userStats.streakDays >= 7) {
        multiplier += 0.5; // 1.5x for 7+ day streak
      } else if (userStats.streakDays >= 3) {
        multiplier += 0.2; // 1.2x for 3+ day streak
      }

      // Quality bonus
      if (userStats.averageQuality >= 0.9) {
        multiplier += 0.5; // High quality user
      } else if (userStats.averageQuality >= 0.7) {
        multiplier += 0.2; // Good quality user
      }

      // Tier multiplier from config
      const tierMultiplier = this.config.creditMultipliers[`tier_${userStats.multiplierTier}`] || 1;
      multiplier *= tierMultiplier;

      // Experience bonus
      if (userStats.totalSubmissions >= 100) {
        bonus += 5; // Expert user bonus
      } else if (userStats.totalSubmissions >= 50) {
        bonus += 2; // Experienced user bonus
      }
    }

    // Quality score bonus
    if (qualityScore && qualityScore >= 0.8) {
      bonus += Math.floor(baseCredits * 0.5); // 50% bonus for high quality
    }

    const finalCredits = Math.floor(baseCredits * multiplier) + bonus;

    return {
      baseCredits,
      multiplier,
      bonus,
      reason: this.buildRewardReason(multiplier, bonus, userStats),
      qualityScore
    };
  }

  /**
   * Build human-readable reward reason
   */
  private buildRewardReason(
    multiplier: number,
    bonus: number,
    userStats?: UserFeedbackStats
  ): string {
    const reasons: string[] = [];

    if (multiplier > 1) {
      if (userStats?.streakDays && userStats.streakDays >= 7) {
        reasons.push(`${userStats.streakDays}-day streak bonus`);
      }
      if (userStats?.averageQuality && userStats.averageQuality >= 0.9) {
        reasons.push('high quality feedback');
      }
      if (userStats?.multiplierTier && userStats.multiplierTier > 1) {
        reasons.push(`tier ${userStats.multiplierTier} multiplier`);
      }
    }

    if (bonus > 0) {
      if (userStats?.totalSubmissions && userStats.totalSubmissions >= 100) {
        reasons.push('expert user bonus');
      }
      reasons.push('quality bonus');
    }

    return reasons.length > 0 
      ? `Earned with ${reasons.join(', ')}`
      : 'Base feedback reward';
  }

  /**
   * Check if user can submit feedback (cooldown, rate limiting)
   */
  async canSubmitFeedback(userId: string, documentId: string): Promise<{
    canSubmit: boolean;
    reason?: string;
    cooldownEndsAt?: Date;
  }> {
    if (!this.config.enabled) {
      return { canSubmit: false, reason: 'Feedback system is disabled' };
    }

    try {
      const response = await fetch(
        `${this.apiEndpoint}/feedback/can-submit/${userId}/${documentId}`
      );
      const data = await response.json();
      
      return {
        canSubmit: data.canSubmit,
        reason: data.reason,
        cooldownEndsAt: data.cooldownEndsAt ? new Date(data.cooldownEndsAt) : undefined
      };
    } catch (error) {
      // If API fails, allow submission (fail open)
      return { canSubmit: true };
    }
  }

  /**
   * Get pending peer validation tasks for a user
   */
  async getPeerValidationTasks(userId: string, limit: number = 5): Promise<FeedbackApiResponse<any[]>> {
    if (!this.config.enabled || !this.config.peerValidationEnabled) {
      return { success: false, error: 'Peer validation is disabled' };
    }

    try {
      const response = await fetch(
        `${this.apiEndpoint}/feedback/peer-validation/${userId}?limit=${limit}`
      );
      const data = await response.json();
      
      if (!response.ok) {
        return { success: false, error: data.error || 'Failed to fetch validation tasks' };
      }

      return { success: true, data: data.tasks };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error'
      };
    }
  }

  /**
   * Enable/disable the feedback system
   */
  setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<FeedbackSystemConfig>): void {
    this.config = { ...this.config, ...newConfig };
    if (newConfig.apiEndpoint) {
      this.apiEndpoint = newConfig.apiEndpoint;
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): FeedbackSystemConfig {
    return { ...this.config };
  }
}