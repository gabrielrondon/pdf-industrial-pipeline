# Feedback System Integration Guide

This guide shows how to integrate the PDF Pipeline Feedback System into your existing application.

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Integration](#basic-integration)
- [Advanced Configuration](#advanced-configuration)
- [API Integration](#api-integration)
- [Database Setup](#database-setup)
- [Credit System Integration](#credit-system-integration)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install the Package

```bash
npm install @pdf-pipeline/feedback-system
```

### 2. Add to Your App

```tsx
import { 
  FeedbackProvider, 
  DocumentFeedback,
  MissingInfoReporter 
} from '@pdf-pipeline/feedback-system';

function App() {
  return (
    <FeedbackProvider>
      <YourExistingApp />
      
      {/* Add feedback to document analysis pages */}
      <DocumentFeedback
        documentId="doc-123"
        documentType="iptu"
        userId="user-456"
        onComplete={(credits) => console.log(`Earned ${credits} credits!`)}
      />
      
      {/* Add missing info reporter */}
      <MissingInfoReporter
        documentId="doc-123"
        userId="user-456"
      />
    </FeedbackProvider>
  );
}
```

### 3. Set Up API Endpoints

Add the feedback API endpoints to your FastAPI backend:

```python
from apps.api.api.v1.feedback import router as feedback_router

app.include_router(feedback_router, prefix="/api/v1")
```

### 4. Run Database Migrations

```bash
psql -d your_database -f apps/api/database/migrations/create_feedback_tables.sql
```

## Installation

### Prerequisites
- Node.js 18+
- React 18+
- PostgreSQL database
- FastAPI backend

### Package Installation

```bash
# In your project root
cd packages/feedback-system
npm install
npm run build

# In your frontend app
npm install @pdf-pipeline/feedback-system
```

## Basic Integration

### Frontend Integration

#### 1. Wrap Your App with FeedbackProvider

```tsx
// In your main App.tsx or _app.tsx
import { FeedbackProvider, DEFAULT_FEEDBACK_CONFIG } from '@pdf-pipeline/feedback-system';

const feedbackConfig = {
  ...DEFAULT_FEEDBACK_CONFIG,
  apiEndpoint: '/api/v1', // Your API base URL
  enabled: true
};

function App() {
  const { user } = useAuth(); // Your auth system
  
  return (
    <FeedbackProvider config={feedbackConfig} userId={user?.id}>
      <Router>
        <Routes>
          {/* Your existing routes */}
        </Routes>
      </Router>
    </FeedbackProvider>
  );
}
```

#### 2. Add Feedback Components to Document Pages

```tsx
// In your document analysis page
import { 
  DocumentFeedback,
  SmartQuickFeedback,
  MissingInfoReporter 
} from '@pdf-pipeline/feedback-system';

function DocumentAnalysisPage({ documentId, analysisResults }) {
  const { user } = useAuth();
  
  return (
    <div>
      {/* Your existing analysis display */}
      <AnalysisResults data={analysisResults} />
      
      {/* Smart feedback based on confidence */}
      <SmartQuickFeedback
        documentId={documentId}
        documentType="property_valuation"
        userId={user.id}
        onComplete={(credits) => {
          toast.success(`You earned ${credits} credits!`);
          // Update user credits in your system
        }}
      />
      
      {/* Missing info reporter */}
      <div className="mt-4 flex justify-end">
        <MissingInfoReporter
          documentId={documentId}
          userId={user.id}
        />
      </div>
    </div>
  );
}
```

#### 3. Add Feedback Prompts to Document Lists

```tsx
// In your document list component
import { FeedbackCreditBanner } from '@/components/credits/FeedbackCreditBanner';

function DocumentList({ documents }) {
  return (
    <div>
      {/* Encourage feedback participation */}
      <FeedbackCreditBanner documentCount={documents.length} />
      
      {/* Your document list */}
      {documents.map(doc => (
        <DocumentCard 
          key={doc.id} 
          document={doc}
          // Add feedback indicator
          showFeedbackPrompt={!doc.user_feedback_submitted}
        />
      ))}
    </div>
  );
}
```

### Backend Integration

#### 1. Include Feedback Router

```python
# In your main FastAPI app (main.py or main_v2.py)
from fastapi import FastAPI
from apps.api.api.v1.feedback import router as feedback_router

app = FastAPI()

# Include the feedback router
app.include_router(feedback_router, prefix="/api/v1")
```

#### 2. Configure Database Connection

The feedback endpoints use your existing database connection from `database.connection.get_db()`.

#### 3. Set Up Background Tasks

```python
# In your app startup
from apps.api.api.v1.feedback import FeedbackIntegrator

@app.on_event("startup")
async def startup_event():
    # Initialize feedback integrator for ML training
    feedback_integrator = FeedbackIntegrator()
    await feedback_integrator.initialize()
```

## Advanced Configuration

### Custom Question Templates

```tsx
// Create custom questions for your document types
import { DocumentQuestionTemplate, FeedbackQuestionType } from '@pdf-pipeline/feedback-system';

const customQuestions: DocumentQuestionTemplate = {
  documentType: DocumentType.CUSTOM_TYPE,
  questions: [
    {
      id: 'custom_accuracy',
      type: FeedbackQuestionType.RATING,
      question: 'How accurate is our custom analysis?',
      required: true,
      creditReward: 8,
      validation: { min: 1, max: 5 }
    }
  ],
  triggerConditions: {
    confidenceThreshold: 0.6
  }
};
```

### Credit System Customization

```tsx
const feedbackConfig = {
  enabled: true,
  apiEndpoint: '/api/v1',
  creditMultipliers: {
    tier_1: 1.0,    // Free users
    tier_2: 1.5,    // Pro users
    tier_3: 2.0,    // Premium users
    tier_4: 2.5     // Expert users
  },
  maxQuestionsPerSession: 5, // Limit questions for free users
  cooldownBetweenSessions: 30, // 30 minutes
  peerValidationEnabled: true,
  gamificationEnabled: true
};
```

### Conditional Feedback Display

```tsx
// Show different feedback based on user plan or document confidence
function ConditionalFeedback({ document, user }) {
  const showDetailedFeedback = document.confidence < 0.7;
  const showQuickFeedback = document.confidence > 0.8;
  const canReportMissing = user.plan !== 'free' || user.feedbackCount < 10;
  
  return (
    <FeedbackIntegration
      documentId={document.id}
      documentType={document.type}
      showQuickFeedback={showQuickFeedback}
      showDetailedFeedback={showDetailedFeedback}
      showMissingInfo={canReportMissing}
      mlPredictions={document.analysis}
    />
  );
}
```

## API Integration

### Frontend API Calls

The package handles API calls automatically, but you can also make direct calls:

```tsx
import { FeedbackService } from '@pdf-pipeline/feedback-system';

const feedbackService = new FeedbackService(config);

// Get questions for a document
const questions = await feedbackService.getFeedbackQuestions(
  documentId,
  documentType,
  mlPredictions,
  userPlan
);

// Submit feedback
const result = await feedbackService.submitFeedback(submission);
```

### Backend API Endpoints

The package provides these endpoints:

- `POST /api/v1/feedback/questions` - Get feedback questions
- `POST /api/v1/feedback/submit` - Submit feedback
- `POST /api/v1/feedback/missing-info` - Report missing info
- `GET /api/v1/feedback/user-stats/{user_id}` - Get user stats
- `GET /api/v1/feedback/can-submit/{user_id}/{document_id}` - Check submission eligibility

## Database Setup

### 1. Run Migrations

```bash
# Apply the feedback system database migrations
psql -d your_database_name -f apps/api/database/migrations/create_feedback_tables.sql
```

### 2. Verify Tables Created

The migration creates these tables:
- `feedback_sessions` - Track user feedback sessions
- `feedback_questions` - Store dynamic questions
- `feedback_submissions` - Complete feedback submissions
- `feedback_answers` - Individual question answers
- `missing_info_reports` - User-reported missing information
- `user_feedback_stats` - User statistics and achievements
- `peer_validation_tasks` - Community validation
- `feedback_ml_training_data` - ML training data

### 3. Configure Permissions

```sql
-- Grant permissions to your API user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_api_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_api_user;
```

## Credit System Integration

### Integrate with Existing Credits

```python
# In your feedback endpoint customization
async def update_user_credits(user_id: str, credits: CreditReward, db: Session):
    total_credits = int(credits.baseCredits * credits.multiplier + credits.bonus)
    
    # Update your existing credit system
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.credits = (user.credits or 0) + total_credits
        
        # Log transaction in your existing system
        create_credit_transaction(
            user_id=user_id,
            type='feedback_earned',
            amount=total_credits,
            reason=credits.reason
        )
        
        db.commit()
```

### Frontend Credit Updates

```tsx
// Listen for credit updates and refresh your credit display
useEffect(() => {
  const handleCreditsUpdated = (event: CustomEvent) => {
    // Refresh user data or credit balance
    refreshUserCredits();
  };

  window.addEventListener('credits-updated', handleCreditsUpdated);
  return () => window.removeEventListener('credits-updated', handleCreditsUpdated);
}, []);
```

## Customization

### Custom Styling

```tsx
// Use your own CSS classes
<DocumentFeedback
  className="my-custom-feedback-styles"
  documentId={documentId}
  documentType={documentType}
  userId={userId}
/>
```

```css
/* Custom feedback styling */
.my-custom-feedback-styles {
  border: 2px solid #your-brand-color;
  border-radius: 12px;
}

.my-custom-feedback-styles .feedback-container {
  background: linear-gradient(135deg, #your-colors);
}
```

### Custom Question Generation

```python
# Override question generation in your API
from apps.api.api.v1.feedback import feedback_integrator

@router.post("/feedback/questions")
async def get_custom_questions(request: QuestionRequest):
    # Your custom logic for generating questions
    questions = await generate_custom_questions(
        request.documentType,
        request.mlPredictions
    )
    
    return QuestionsResponse(questions=questions)
```

### Custom Credit Calculation

```python
def custom_credit_calculation(submission: FeedbackSubmission, user_stats: UserFeedbackStats):
    # Your custom credit logic
    base_credits = calculate_custom_base_credits(submission)
    multiplier = get_user_multiplier(user_stats, submission.userId)
    
    return CreditReward(
        baseCredits=base_credits,
        multiplier=multiplier,
        bonus=calculate_bonus(submission),
        reason="Custom calculation"
    )
```

## Troubleshooting

### Common Issues

#### 1. API Endpoints Not Working

```bash
# Check if the feedback router is included
curl -X POST http://localhost:8000/api/v1/feedback/questions
```

**Solution:** Ensure the feedback router is included in your main FastAPI app.

#### 2. Database Connection Issues

```python
# Test database connection
from database.connection import get_db

def test_db():
    db = next(get_db())
    result = db.execute("SELECT 1").fetchone()
    print("Database connected:", result)
```

#### 3. Frontend Package Not Found

```bash
# Rebuild the package
cd packages/feedback-system
npm run build

# Reinstall in your app
cd apps/client-frontend
npm install @pdf-pipeline/feedback-system
```

#### 4. Credit Updates Not Working

Check that your event listener is properly set up:

```tsx
// Make sure event listener is added
window.addEventListener('credits-updated', handleCreditsUpdated);
```

### Performance Considerations

1. **Limit Questions per Session**: Set `maxQuestionsPerSession` based on user plan
2. **Implement Caching**: Cache questions for better performance
3. **Background Processing**: Use background tasks for ML training
4. **Rate Limiting**: Implement cooldowns to prevent spam

### Security Notes

1. **Validate User Permissions**: Always check if user can submit feedback
2. **Sanitize Input**: Validate all user input in feedback submissions
3. **Rate Limiting**: Implement proper rate limiting on feedback endpoints
4. **API Authentication**: Ensure feedback endpoints require authentication

## Easy Removal

To remove the feedback system:

### 1. Remove Frontend Integration

```tsx
// Remove FeedbackProvider and components
// Remove feedback-related imports
// Remove event listeners
```

### 2. Remove API Endpoints

```python
# Comment out or remove the feedback router
# app.include_router(feedback_router, prefix="/api/v1")
```

### 3. Remove Database Tables (Optional)

```sql
-- Drop feedback tables if you want to remove completely
DROP TABLE IF EXISTS feedback_ml_training_data;
DROP TABLE IF EXISTS peer_validation_tasks;
DROP TABLE IF EXISTS user_feedback_stats;
DROP TABLE IF EXISTS missing_info_reports;
DROP TABLE IF EXISTS feedback_answers;
DROP TABLE IF EXISTS feedback_submissions;
DROP TABLE IF EXISTS feedback_questions;
DROP TABLE IF EXISTS feedback_sessions;
```

### 4. Uninstall Package

```bash
npm uninstall @pdf-pipeline/feedback-system
```

The modular design ensures clean removal without affecting your core application functionality.