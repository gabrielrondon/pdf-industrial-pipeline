-- Enhanced Feedback System Database Tables
-- Migration for comprehensive user feedback and ML improvement system

-- Create feedback_sessions table for tracking user feedback sessions
CREATE TABLE IF NOT EXISTS feedback_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    is_complete BOOLEAN DEFAULT FALSE,
    credits_earned INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create feedback_questions table for storing dynamic questions
CREATE TABLE IF NOT EXISTS feedback_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id VARCHAR(255) UNIQUE NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- yes_no, rating, text_input, etc.
    question_text TEXT NOT NULL,
    document_type VARCHAR(50),
    required BOOLEAN DEFAULT FALSE,
    credit_reward INTEGER DEFAULT 0,
    options JSONB, -- For multiple choice/select questions
    validation_rules JSONB, -- min, max, pattern validation
    help_text TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create feedback_submissions table for storing user feedback
CREATE TABLE IF NOT EXISTS feedback_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES feedback_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL, -- quick_question, detailed_input, etc.
    submission_data JSONB NOT NULL, -- Complete feedback data
    quality_score DECIMAL(3,2), -- 0.00 to 1.00
    credits_awarded INTEGER DEFAULT 0,
    credit_multiplier DECIMAL(3,2) DEFAULT 1.00,
    bonus_credits INTEGER DEFAULT 0,
    reward_reason TEXT,
    processed_for_ml BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create feedback_answers table for individual question responses
CREATE TABLE IF NOT EXISTS feedback_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    question_id VARCHAR(255) NOT NULL,
    answer_value JSONB NOT NULL, -- Stores any type of answer (string, number, boolean)
    confidence DECIMAL(3,2), -- User confidence in their answer (0.00 to 1.00)
    time_spent INTEGER, -- Seconds spent on this question
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create missing_info_reports table for user-reported missing information
CREATE TABLE IF NOT EXISTS missing_info_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- financial, legal, property_details, etc.
    description TEXT NOT NULL,
    specific_field VARCHAR(255),
    suggested_value TEXT,
    severity VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    credits_awarded INTEGER DEFAULT 0,
    quality_score DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'pending', -- pending, reviewed, implemented, rejected
    reviewer_notes TEXT,
    processed_for_ml BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create user_feedback_stats table for tracking user feedback statistics
CREATE TABLE IF NOT EXISTS user_feedback_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_submissions INTEGER DEFAULT 0,
    total_credits_earned INTEGER DEFAULT 0,
    average_quality_score DECIMAL(3,2) DEFAULT 0.00,
    feedback_streak_days INTEGER DEFAULT 0,
    last_feedback_date DATE,
    multiplier_tier INTEGER DEFAULT 1,
    badges JSONB DEFAULT '[]', -- Array of earned badges
    achievements JSONB DEFAULT '{}', -- Achievement tracking
    peer_validations_completed INTEGER DEFAULT 0,
    peer_validation_accuracy DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create peer_validation_tasks table for community validation
CREATE TABLE IF NOT EXISTS peer_validation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_submission_id UUID NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    original_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    validator_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    validation_result VARCHAR(20), -- agree, disagree, partial
    validation_notes TEXT,
    credits_awarded INTEGER DEFAULT 0,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days')
);

-- Create feedback_ml_training_data table for ML improvement tracking
CREATE TABLE IF NOT EXISTS feedback_ml_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    training_features JSONB NOT NULL, -- Features extracted for training
    target_scores JSONB NOT NULL, -- Target values derived from feedback
    ml_model_version VARCHAR(50),
    training_weight DECIMAL(3,2) DEFAULT 1.00, -- Weight for this feedback in training
    integrated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_feedback_sessions_user_id ON feedback_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_sessions_document_id ON feedback_sessions(document_id);
CREATE INDEX IF NOT EXISTS idx_feedback_sessions_started_at ON feedback_sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_feedback_submissions_user_id ON feedback_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_document_id ON feedback_submissions(document_id);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_submitted_at ON feedback_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_processed_ml ON feedback_submissions(processed_for_ml);

CREATE INDEX IF NOT EXISTS idx_feedback_answers_submission_id ON feedback_answers(submission_id);
CREATE INDEX IF NOT EXISTS idx_feedback_answers_question_id ON feedback_answers(question_id);

CREATE INDEX IF NOT EXISTS idx_missing_info_reports_user_id ON missing_info_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_missing_info_reports_document_id ON missing_info_reports(document_id);
CREATE INDEX IF NOT EXISTS idx_missing_info_reports_status ON missing_info_reports(status);
CREATE INDEX IF NOT EXISTS idx_missing_info_reports_processed_ml ON missing_info_reports(processed_for_ml);

CREATE INDEX IF NOT EXISTS idx_user_feedback_stats_user_id ON user_feedback_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_stats_last_feedback ON user_feedback_stats(last_feedback_date);

CREATE INDEX IF NOT EXISTS idx_peer_validation_validator ON peer_validation_tasks(validator_user_id);
CREATE INDEX IF NOT EXISTS idx_peer_validation_expires ON peer_validation_tasks(expires_at);

CREATE INDEX IF NOT EXISTS idx_feedback_ml_training_document ON feedback_ml_training_data(document_id);
CREATE INDEX IF NOT EXISTS idx_feedback_ml_training_integrated ON feedback_ml_training_data(integrated_at);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_feedback_sessions_updated_at 
    BEFORE UPDATE ON feedback_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_feedback_stats_updated_at 
    BEFORE UPDATE ON user_feedback_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update user feedback stats
CREATE OR REPLACE FUNCTION update_user_feedback_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update stats when new feedback is submitted
    INSERT INTO user_feedback_stats (user_id, total_submissions, total_credits_earned, last_feedback_date)
    VALUES (NEW.user_id, 1, NEW.credits_awarded, CURRENT_DATE)
    ON CONFLICT (user_id)
    DO UPDATE SET
        total_submissions = user_feedback_stats.total_submissions + 1,
        total_credits_earned = user_feedback_stats.total_credits_earned + NEW.credits_awarded,
        last_feedback_date = CURRENT_DATE,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_user_feedback_stats
    AFTER INSERT ON feedback_submissions
    FOR EACH ROW EXECUTE FUNCTION update_user_feedback_stats();

-- Function to calculate and update quality scores
CREATE OR REPLACE FUNCTION calculate_average_quality()
RETURNS TRIGGER AS $$
DECLARE
    avg_quality DECIMAL(3,2);
BEGIN
    -- Calculate average quality score for the user
    SELECT AVG(quality_score)
    INTO avg_quality
    FROM feedback_submissions
    WHERE user_id = NEW.user_id AND quality_score IS NOT NULL;
    
    -- Update user stats with new average
    UPDATE user_feedback_stats
    SET average_quality_score = COALESCE(avg_quality, 0.00)
    WHERE user_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_calculate_average_quality
    AFTER INSERT OR UPDATE ON feedback_submissions
    FOR EACH ROW EXECUTE FUNCTION calculate_average_quality();

-- Insert default feedback questions for different document types
INSERT INTO feedback_questions (question_id, question_type, question_text, document_type, required, credit_reward, help_text) VALUES
-- IPTU questions
('iptu_found', 'yes_no', 'Did you find IPTU information in this document?', 'iptu', true, 5, 'IPTU (property tax) information includes tax amounts, payment status, or property code'),
('iptu_amount', 'currency', 'If found, what is the IPTU amount?', 'iptu', false, 10, 'Enter the annual IPTU tax amount if mentioned'),
('iptu_status', 'select', 'What is the IPTU payment status?', 'iptu', false, 5, null),

-- Property valuation questions
('valuation_accuracy', 'rating', 'How accurate does the AI property valuation seem?', 'property_valuation', true, 5, 'Rate from 1 (way off) to 5 (very accurate)'),
('market_value_opinion', 'select', 'Based on your knowledge, the estimated market value is:', 'property_valuation', false, 8, null),
('additional_liens', 'yes_no', 'Did you notice any liens or debts not captured by the AI?', 'property_valuation', false, 12, 'Mortgages, liens, outstanding debts, or legal encumbrances'),

-- Risk assessment questions
('risk_level_opinion', 'select', 'The AI risk assessment seems:', 'risk_assessment', true, 5, null),
('missing_risk_factors', 'yes_no', 'Are there risk factors the AI missed?', 'risk_assessment', false, 10, null),
('investment_decision', 'select', 'Would you personally invest in this property?', 'risk_assessment', false, 8, null),

-- General quality questions
('overall_analysis_quality', 'rating', 'Overall quality of AI analysis', null, true, 5, null),
('missed_important_info', 'yes_no', 'Did the AI miss any important information?', null, false, 10, null)

ON CONFLICT (question_id) DO NOTHING;

-- Insert options for select questions
UPDATE feedback_questions SET options = '["Current/Paid", "Overdue", "Partially paid", "Unknown", "Not mentioned"]'::jsonb 
WHERE question_id = 'iptu_status';

UPDATE feedback_questions SET options = '["Too low", "About right", "Too high", "Need more info"]'::jsonb 
WHERE question_id = 'market_value_opinion';

UPDATE feedback_questions SET options = '["Too conservative", "About right", "Too optimistic", "Incomplete"]'::jsonb 
WHERE question_id = 'risk_level_opinion';

UPDATE feedback_questions SET options = '["Definitely yes", "Probably yes", "Maybe", "Probably no", "Definitely no"]'::jsonb 
WHERE question_id = 'investment_decision';

-- Set validation rules for rating questions
UPDATE feedback_questions SET validation_rules = '{"min": 1, "max": 5}'::jsonb 
WHERE question_type = 'rating';

COMMENT ON TABLE feedback_sessions IS 'Tracks user feedback sessions for document analysis';
COMMENT ON TABLE feedback_questions IS 'Stores dynamic feedback questions for different document types';
COMMENT ON TABLE feedback_submissions IS 'Stores complete feedback submissions from users';
COMMENT ON TABLE feedback_answers IS 'Stores individual answers to feedback questions';
COMMENT ON TABLE missing_info_reports IS 'User reports of information missed by AI';
COMMENT ON TABLE user_feedback_stats IS 'Aggregated feedback statistics per user';
COMMENT ON TABLE peer_validation_tasks IS 'Community validation tasks for feedback quality';
COMMENT ON TABLE feedback_ml_training_data IS 'Processed feedback data for ML model training';