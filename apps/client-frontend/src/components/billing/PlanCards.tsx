
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlan } from '@/contexts/PlanContext';
import { useAuth } from '@/contexts/AuthContext';
import { UserPlan } from '@/types';
import { toast } from 'sonner';
import { PlanCard } from './PlanCard';
import { PlanComparison } from './PlanComparison';
import { getActionType } from './utils/planUtils';

interface PlanCardsProps {
  showCompare?: boolean;
  onPlanSelected?: (plan: UserPlan) => void;
}

export function PlanCards({ showCompare = true, onPlanSelected }: PlanCardsProps) {
  const { currentPlan, planDetails, createCheckoutSession, createUpgrade, calculateUpgradePrice, isLoadingPlan } = usePlan();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState<UserPlan | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [upgradeAmounts, setUpgradeAmounts] = useState<Record<string, number | null>>({});

  // Calculate upgrade amounts for each plan
  useEffect(() => {
    if (user && currentPlan !== 'free') {
      const loadUpgradeAmounts = async () => {
        const amounts: Record<string, number | null> = {};
        for (const plan of planDetails) {
          if (plan.id !== currentPlan && plan.id !== 'free') {
            amounts[plan.id] = await calculateUpgradePrice(plan.id);
          }
        }
        setUpgradeAmounts(amounts);
      };
      loadUpgradeAmounts();
    }
  }, [currentPlan, user, calculateUpgradePrice, planDetails]);

  const handleSelectPlan = (plan: UserPlan) => {
    if (onPlanSelected) {
      onPlanSelected(plan);
    } else {
      setSelectedPlan(plan);
    }
  };

  const handlePlanAction = async (planId: UserPlan) => {
    if (!user) {
      navigate('/login', { state: { selectedPlan: planId } });
      return;
    }

    if (planId === 'free') {
      toast.success('Você está no plano gratuito!');
      return;
    }

    const actionType = getActionType(planId, currentPlan, user);
    
    if (actionType === 'current') {
      toast.info('Você já está neste plano!');
      return;
    }

    try {
      setIsRedirecting(true);
      
      if (actionType === 'subscribe') {
        // New subscription
        toast.loading('Redirecionando para o checkout...', { id: 'checkout' });
        const checkoutUrl = await createCheckoutSession(planId);
        toast.dismiss('checkout');
        toast.success('Redirecionando para o Stripe...');
        window.open(checkoutUrl, '_blank');
      } else {
        // Upgrade or downgrade existing subscription
        toast.loading('Processando alteração do plano...', { id: 'upgrade' });
        const result = await createUpgrade(planId);
        toast.dismiss('upgrade');
        
        if (result.success) {
          toast.success(result.message);
        } else {
          toast.error('Erro ao alterar plano. Tente novamente.');
        }
      }
    } catch (error) {
      console.error('Failed to process plan action:', error);
      toast.dismiss('checkout');
      toast.dismiss('upgrade');
      toast.error('Erro ao processar solicitação. Tente novamente.');
    } finally {
      setIsRedirecting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="grid md:grid-cols-3 gap-6">
        {planDetails.map((plan) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            currentPlan={currentPlan}
            user={user}
            selectedPlan={selectedPlan}
            upgradeAmounts={upgradeAmounts}
            isLoadingPlan={isLoadingPlan}
            isRedirecting={isRedirecting}
            onSelectPlan={handleSelectPlan}
            onPlanAction={handlePlanAction}
          />
        ))}
      </div>
      
      {showCompare && <PlanComparison planDetails={planDetails} />}
    </div>
  );
}
