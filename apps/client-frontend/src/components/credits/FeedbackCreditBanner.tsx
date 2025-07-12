import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Coins, MessageSquare, Star, Flag } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface FeedbackCreditBannerProps {
  documentCount?: number;
  className?: string;
}

export const FeedbackCreditBanner: React.FC<FeedbackCreditBannerProps> = ({
  documentCount = 0,
  className = ''
}) => {
  const { user } = useAuth();
  const [recentEarnings, setRecentEarnings] = useState<number>(0);
  const [showBanner, setShowBanner] = useState(true);

  // Listen for credit updates from feedback system
  useEffect(() => {
    const handleCreditsUpdated = (event: CustomEvent) => {
      if (event.detail?.earned) {
        setRecentEarnings(prev => prev + event.detail.earned);
        
        // Auto-hide after showing recent earnings
        setTimeout(() => {
          setRecentEarnings(0);
        }, 5000);
      }
    };

    window.addEventListener('credits-updated', handleCreditsUpdated as EventListener);
    
    return () => {
      window.removeEventListener('credits-updated', handleCreditsUpdated as EventListener);
    };
  }, []);

  // Don't show if user has premium plan or banner is dismissed
  if (!user || user.plan === 'premium' || !showBanner) {
    return null;
  }

  const canEarnCredits = documentCount > 0;
  const isPaidPlan = user.plan !== 'free';

  return (
    <Card className={`feedback-credit-banner bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {/* Recent earnings display */}
            {recentEarnings > 0 && (
              <div className="mb-3 p-2 bg-green-100 border border-green-200 rounded-md">
                <div className="flex items-center gap-2">
                  <Coins className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">
                    🎉 You just earned {recentEarnings} credits!
                  </span>
                </div>
              </div>
            )}

            {/* Main banner content */}
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <MessageSquare className="h-5 w-5 text-blue-600" />
              </div>
              
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">
                  Earn Credits by Helping Our AI Learn
                </h3>
                
                <p className="text-sm text-gray-600 mb-3">
                  {canEarnCredits 
                    ? 'Share feedback on your document analyses and earn credits for future use!'
                    : 'Upload documents and provide feedback to start earning credits!'
                  }
                </p>

                {/* Credit earning opportunities */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                  <div className="flex items-center gap-2 text-xs">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span className="text-gray-600">Quick ratings: +3-5 credits</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-xs">
                    <MessageSquare className="h-3 w-3 text-blue-500" />
                    <span className="text-gray-600">Detailed feedback: +8-15 credits</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-xs">
                    <Flag className="h-3 w-3 text-orange-500" />
                    <span className="text-gray-600">Report missing info: +15 credits</span>
                  </div>
                </div>

                {/* Plan-specific benefits */}
                {isPaidPlan && (
                  <div className="flex items-center gap-2 mb-3">
                    <Badge variant="secondary" className="text-xs">
                      {user.plan.toUpperCase()} BONUS
                    </Badge>
                    <span className="text-xs text-gray-600">
                      {user.plan === 'pro' ? '1.5x' : '2x'} credit multiplier on all feedback
                    </span>
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex gap-2">
                  {canEarnCredits && (
                    <Button
                      size="sm"
                      onClick={() => {
                        // Scroll to documents or show feedback modal
                        const docSection = document.querySelector('[data-documents-section]');
                        docSection?.scrollIntoView({ behavior: 'smooth' });
                      }}
                      className="text-xs"
                    >
                      Start Earning Credits
                    </Button>
                  )}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowBanner(false)}
                    className="text-xs"
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Close button */}
          <button
            onClick={() => setShowBanner(false)}
            className="text-gray-400 hover:text-gray-600 ml-2"
          >
            ✕
          </button>
        </div>
      </CardContent>
    </Card>
  );
};