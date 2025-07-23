import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserPlan, PlanDetails } from '@/types';
import { useAuth } from './AuthContext';
import { supabase } from '@/integrations/supabase/client';

interface PlanContextType {
  currentPlan: UserPlan;
  planDetails: PlanDetails[];
  isLoadingPlan: boolean;
  createCheckoutSession: (planId: UserPlan) => Promise<string>;
  createUpgrade: (planId: UserPlan) => Promise<{ success: boolean; message: string; prorationAmount?: number }>;
  openCustomerPortal: () => Promise<string>;
  refreshPlanDetails: () => Promise<void>;
  calculateUpgradePrice: (targetPlan: UserPlan) => Promise<number | null>;
}

const PLAN_DETAILS: PlanDetails[] = [
  {
    id: 'free',
    name: 'Gratuito',
    price: 0,
    credits: 100,
    description: 'Para experimentar a plataforma',
    color: 'bg-gray-100 border-gray-300',
    features: [
      { title: 'Upload de PDF para análise', free: true, pro: true, premium: true },
      { title: 'Visualização de relatório da análise', free: true, pro: true, premium: true },
      { title: 'Escolher tornar o lead privado', free: false, pro: true, premium: true },
      { title: 'Compartilhar lead com base', free: true, pro: true, premium: true },
      { title: 'Receber leads da comunidade', free: false, pro: false, premium: true },
      { title: 'Ganhar créditos por compartilhamento', free: false, pro: true, premium: true },
      { title: 'Histórico de documentos', free: true, pro: true, premium: true },
      { title: 'Dashboard com estatísticas', free: true, pro: true, premium: true },
      { title: 'Notificações por Email', free: false, pro: true, premium: true },
      { title: 'Notificações por SMS', free: false, pro: false, premium: true },
      { title: 'Suporte prioritário', free: false, pro: false, premium: true },
    ]
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 39,
    credits: 1000,
    description: 'Para usuários frequentes',
    color: 'bg-blue-50 border-blue-500',
    features: [
      { title: 'Upload de PDF para análise', free: true, pro: true, premium: true },
      { title: 'Visualização de relatório da análise', free: true, pro: true, premium: true },
      { title: 'Escolher tornar o lead privado', free: false, pro: true, premium: true },
      { title: 'Compartilhar lead com base', free: true, pro: true, premium: true },
      { title: 'Receber leads da comunidade', free: false, pro: false, premium: true },
      { title: 'Ganhar créditos por compartilhamento', free: false, pro: true, premium: true },
      { title: 'Histórico de documentos', free: true, pro: true, premium: true },
      { title: 'Dashboard com estatísticas', free: true, pro: true, premium: true },
      { title: 'Notificações por Email', free: false, pro: true, premium: true },
      { title: 'Notificações por SMS', free: false, pro: false, premium: true },
      { title: 'Suporte prioritário', free: false, pro: false, premium: true },
    ]
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 99,
    credits: 5000,
    description: 'Para profissionais e empresas',
    color: 'bg-purple-50 border-purple-500',
    recommended: true,
    features: [
      { title: 'Upload de PDF para análise', free: true, pro: true, premium: true },
      { title: 'Visualização de relatório da análise', free: true, pro: true, premium: true },
      { title: 'Escolher tornar o lead privado', free: false, pro: true, premium: true },
      { title: 'Compartilhar lead com base', free: true, pro: true, premium: true },
      { title: 'Receber leads da comunidade', free: false, pro: false, premium: true },
      { title: 'Ganhar créditos por compartilhamento', free: false, pro: true, premium: true },
      { title: 'Histórico de documentos', free: true, pro: true, premium: true },
      { title: 'Dashboard com estatísticas', free: true, pro: true, premium: true },
      { title: 'Notificações por Email', free: false, pro: true, premium: true },
      { title: 'Notificações por SMS', free: false, pro: false, premium: true },
      { title: 'Suporte prioritário', free: false, pro: false, premium: true },
    ]
  }
];

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useAuth();
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

  const createCheckoutSession = async (planId: UserPlan): Promise<string> => {
    if (planId === 'free') {
      throw new Error('Cannot create checkout for free plan');
    }

    setIsLoadingPlan(true);
    try {
      const { data, error } = await supabase.functions.invoke('create-checkout', {
        body: { planId }
      });

      if (error) {
        console.error('Error creating checkout session:', error);
        throw error;
      }

      return data.url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      throw error;
    } finally {
      setIsLoadingPlan(false);
    }
  };

  const createUpgrade = async (planId: UserPlan): Promise<{ success: boolean; message: string; prorationAmount?: number }> => {
    if (planId === 'free') {
      throw new Error('Cannot upgrade to free plan');
    }

    setIsLoadingPlan(true);
    try {
      const { data, error } = await supabase.functions.invoke('create-upgrade', {
        body: { planId }
      });

      if (error) {
        console.error('Error creating upgrade:', error);
        throw error;
      }

      // Refresh plan details after successful upgrade
      setTimeout(() => {
        refreshPlanDetails();
      }, 2000);

      return {
        success: data.success,
        message: data.message,
        prorationAmount: data.prorationAmount
      };
    } catch (error) {
      console.error('Failed to create upgrade:', error);
      throw error;
    } finally {
      setIsLoadingPlan(false);
    }
  };

  const calculateUpgradePrice = async (targetPlan: UserPlan): Promise<number | null> => {
    if (!user || user.plan === 'free' || targetPlan === 'free') {
      return null;
    }

    try {
      const { data, error } = await supabase.functions.invoke('calculate-proration', {
        body: { targetPlan }
      });

      if (error) {
        console.error('Error calculating proration:', error);
        return null;
      }

      return data.prorationAmount;
    } catch (error) {
      console.error('Failed to calculate proration:', error);
      return null;
    }
  };

  const openCustomerPortal = async (): Promise<string> => {
    setIsLoadingPlan(true);
    try {
      const { data, error } = await supabase.functions.invoke('customer-portal');

      if (error) {
        console.error('Error opening customer portal:', error);
        throw error;
      }

      return data.url;
    } catch (error) {
      console.error('Failed to open customer portal:', error);
      throw error;
    } finally {
      setIsLoadingPlan(false);
    }
  };

  const refreshPlanDetails = async (): Promise<void> => {
    if (!user) return;

    setIsLoadingPlan(true);
    try {
      const { data, error } = await supabase.functions.invoke('check-subscription');
      
      if (error) {
        console.error('Error checking subscription:', error);
        return;
      }

      console.log('Subscription status updated:', data);
    } catch (error) {
      console.error('Failed to refresh plan details:', error);
    } finally {
      setIsLoadingPlan(false);
    }
  };

  // Auto-refresh subscription status when user changes
  useEffect(() => {
    if (user) {
      refreshPlanDetails();
    }
  }, [user]);

  // Check for URL parameters that indicate return from Stripe
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true' || urlParams.get('canceled') === 'true') {
      // User returned from Stripe, refresh subscription status
      if (user) {
        console.log('User returned from Stripe, refreshing subscription status...');
        setTimeout(() => {
          refreshPlanDetails();
        }, 2000); // Wait 2 seconds for Stripe webhook to process
      }
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [user]);

  // Periodic refresh when on plans page
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    let interval: NodeJS.Timeout;
    
    if (window.location.pathname === '/plans' && user) {
      // Refresh every 10 seconds when on plans page
      interval = setInterval(() => {
        refreshPlanDetails();
      }, 10000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [user]);

  return (
    <PlanContext.Provider
      value={{
        currentPlan: user?.plan || 'free',
        planDetails: PLAN_DETAILS,
        isLoadingPlan,
        createCheckoutSession,
        createUpgrade,
        openCustomerPortal,
        refreshPlanDetails,
        calculateUpgradePrice,
      }}
    >
      {children}
    </PlanContext.Provider>
  );
};

export const usePlan = (): PlanContextType => {
  const context = useContext(PlanContext);
  if (context === undefined) {
    throw new Error('usePlan must be used within a PlanProvider');
  }
  return context;
};
