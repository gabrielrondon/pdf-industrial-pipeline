import { DocumentType, FeedbackQuestion, FeedbackQuestionType, DocumentQuestionTemplate } from './index';

// Pre-built question templates for each document type
export const IPTU_QUESTIONS: FeedbackQuestion[] = [
  {
    id: 'iptu_found',
    type: FeedbackQuestionType.YES_NO,
    question: 'Did you find IPTU information in this document?',
    required: true,
    creditReward: 5,
    helpText: 'IPTU (property tax) information includes tax amounts, payment status, or property code'
  },
  {
    id: 'iptu_amount',
    type: FeedbackQuestionType.CURRENCY,
    question: 'If found, what is the IPTU amount?',
    required: false,
    creditReward: 10,
    placeholder: 'R$ 0,00',
    helpText: 'Enter the annual IPTU tax amount if mentioned'
  },
  {
    id: 'iptu_status',
    type: FeedbackQuestionType.SELECT,
    question: 'What is the IPTU payment status?',
    required: false,
    creditReward: 5,
    options: ['Current/Paid', 'Overdue', 'Partially paid', 'Unknown', 'Not mentioned']
  },
  {
    id: 'property_code',
    type: FeedbackQuestionType.TEXT_INPUT,
    question: 'Property registration code (if found)',
    required: false,
    creditReward: 8,
    placeholder: 'Enter property code or registration number',
    validation: {
      pattern: '^[0-9.-]+$'
    }
  }
];

export const PROPERTY_VALUATION_QUESTIONS: FeedbackQuestion[] = [
  {
    id: 'valuation_accuracy',
    type: FeedbackQuestionType.RATING,
    question: 'How accurate does the AI property valuation seem?',
    required: true,
    creditReward: 5,
    helpText: 'Rate from 1 (way off) to 5 (very accurate)',
    validation: { min: 1, max: 5 }
  },
  {
    id: 'market_value_opinion',
    type: FeedbackQuestionType.SELECT,
    question: 'Based on your knowledge, the estimated market value is:',
    required: false,
    creditReward: 8,
    options: ['Too low', 'About right', 'Too high', 'Need more info']
  },
  {
    id: 'additional_liens',
    type: FeedbackQuestionType.YES_NO,
    question: 'Did you notice any liens or debts not captured by the AI?',
    required: false,
    creditReward: 12,
    helpText: 'Mortgages, liens, outstanding debts, or legal encumbrances'
  },
  {
    id: 'lien_details',
    type: FeedbackQuestionType.TEXT_INPUT,
    question: 'If yes, describe the additional liens or debts:',
    required: false,
    creditReward: 15,
    placeholder: 'Describe what the AI missed...',
    validation: { min: 10, max: 300 }
  }
];

export const RISK_ASSESSMENT_QUESTIONS: FeedbackQuestion[] = [
  {
    id: 'risk_level_opinion',
    type: FeedbackQuestionType.SELECT,
    question: 'The AI risk assessment seems:',
    required: true,
    creditReward: 5,
    options: ['Too conservative', 'About right', 'Too optimistic', 'Incomplete']
  },
  {
    id: 'missing_risk_factors',
    type: FeedbackQuestionType.YES_NO,
    question: 'Are there risk factors the AI missed?',
    required: false,
    creditReward: 10
  },
  {
    id: 'risk_factor_details',
    type: FeedbackQuestionType.TEXT_INPUT,
    question: 'What risk factors were overlooked?',
    required: false,
    creditReward: 15,
    placeholder: 'Environmental, legal, financial, or other risks...',
    validation: { min: 15, max: 400 }
  },
  {
    id: 'investment_decision',
    type: FeedbackQuestionType.SELECT,
    question: 'Would you personally invest in this property?',
    required: false,
    creditReward: 8,
    options: ['Definitely yes', 'Probably yes', 'Maybe', 'Probably no', 'Definitely no']
  }
];

export const JUDICIAL_AUCTION_QUESTIONS: FeedbackQuestion[] = [
  {
    id: 'auction_type_correct',
    type: FeedbackQuestionType.YES_NO,
    question: 'Is the auction type classification correct?',
    required: true,
    creditReward: 5,
    helpText: 'Judicial vs extrajudicial auction identification'
  },
  {
    id: 'minimum_bid_found',
    type: FeedbackQuestionType.YES_NO,
    question: 'Did you find minimum bid information?',
    required: false,
    creditReward: 8
  },
  {
    id: 'minimum_bid_amount',
    type: FeedbackQuestionType.CURRENCY,
    question: 'What is the minimum bid amount?',
    required: false,
    creditReward: 12,
    placeholder: 'R$ 0,00'
  },
  {
    id: 'auction_date',
    type: FeedbackQuestionType.TEXT_INPUT,
    question: 'Auction date (if mentioned)',
    required: false,
    creditReward: 6,
    placeholder: 'DD/MM/YYYY or as written in document'
  },
  {
    id: 'legal_compliance',
    type: FeedbackQuestionType.RATING,
    question: 'How well does this auction comply with CPC Article 889?',
    required: false,
    creditReward: 10,
    helpText: 'Rate legal compliance from 1 (poor) to 5 (excellent)',
    validation: { min: 1, max: 5 }
  }
];

export const GENERAL_QUALITY_QUESTIONS: FeedbackQuestion[] = [
  {
    id: 'overall_analysis_quality',
    type: FeedbackQuestionType.RATING,
    question: 'Overall quality of AI analysis',
    required: true,
    creditReward: 5,
    validation: { min: 1, max: 5 }
  },
  {
    id: 'missed_important_info',
    type: FeedbackQuestionType.YES_NO,
    question: 'Did the AI miss any important information?',
    required: false,
    creditReward: 10
  },
  {
    id: 'most_useful_finding',
    type: FeedbackQuestionType.TEXT_INPUT,
    question: 'What was the most useful finding in this analysis?',
    required: false,
    creditReward: 8,
    placeholder: 'The most valuable insight was...',
    validation: { min: 10, max: 200 }
  }
];

// Document type to question template mapping
export const DOCUMENT_QUESTION_TEMPLATES: DocumentQuestionTemplate[] = [
  {
    documentType: DocumentType.IPTU,
    questions: [...IPTU_QUESTIONS, ...GENERAL_QUALITY_QUESTIONS],
    triggerConditions: {
      confidenceThreshold: 0.7
    }
  },
  {
    documentType: DocumentType.PROPERTY_VALUATION,
    questions: [...PROPERTY_VALUATION_QUESTIONS, ...GENERAL_QUALITY_QUESTIONS],
    triggerConditions: {
      confidenceThreshold: 0.6
    }
  },
  {
    documentType: DocumentType.RISK_ASSESSMENT,
    questions: [...RISK_ASSESSMENT_QUESTIONS, ...GENERAL_QUALITY_QUESTIONS],
    triggerConditions: {
      confidenceThreshold: 0.65
    }
  },
  {
    documentType: DocumentType.JUDICIAL_AUCTION,
    questions: [...JUDICIAL_AUCTION_QUESTIONS, ...GENERAL_QUALITY_QUESTIONS],
    triggerConditions: {
      confidenceThreshold: 0.75
    }
  }
];

// Quick feedback templates for high-confidence predictions
export const QUICK_VALIDATION_QUESTIONS: Record<DocumentType, FeedbackQuestion[]> = {
  [DocumentType.IPTU]: [
    {
      id: 'quick_iptu_correct',
      type: FeedbackQuestionType.YES_NO,
      question: 'IPTU info looks correct?',
      required: true,
      creditReward: 3
    }
  ],
  [DocumentType.PROPERTY_VALUATION]: [
    {
      id: 'quick_valuation_reasonable',
      type: FeedbackQuestionType.YES_NO,
      question: 'Property value seems reasonable?',
      required: true,
      creditReward: 3
    }
  ],
  [DocumentType.RISK_ASSESSMENT]: [
    {
      id: 'quick_risk_appropriate',
      type: FeedbackQuestionType.YES_NO,
      question: 'Risk level seems appropriate?',
      required: true,
      creditReward: 3
    }
  ],
  [DocumentType.JUDICIAL_AUCTION]: [
    {
      id: 'quick_auction_details_correct',
      type: FeedbackQuestionType.YES_NO,
      question: 'Auction details look correct?',
      required: true,
      creditReward: 3
    }
  ],
  [DocumentType.LEGAL_DOCUMENT]: [
    {
      id: 'quick_legal_analysis_correct',
      type: FeedbackQuestionType.YES_NO,
      question: 'Legal analysis seems accurate?',
      required: true,
      creditReward: 3
    }
  ],
  [DocumentType.FINANCIAL_STATEMENT]: [
    {
      id: 'quick_financial_extraction_correct',
      type: FeedbackQuestionType.YES_NO,
      question: 'Financial data extraction looks right?',
      required: true,
      creditReward: 3
    }
  ]
};