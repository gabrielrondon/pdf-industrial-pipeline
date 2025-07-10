
import { UserPlan, PlanDetails } from '@/types';

export const planPrices = { free: 0, pro: 39, premium: 99 };

export const getActionType = (
  planId: UserPlan, 
  currentPlan: UserPlan, 
  user: any
): 'subscribe' | 'upgrade' | 'downgrade' | 'current' => {
  if (!user || currentPlan === 'free') return 'subscribe';
  if (currentPlan === planId) return 'current';
  
  const currentPrice = planPrices[currentPlan];
  const targetPrice = planPrices[planId];
  
  if (targetPrice > currentPrice) return 'upgrade';
  if (targetPrice < currentPrice) return 'downgrade';
  return 'current';
};

export const getButtonText = (
  planDetail: PlanDetails,
  actionType: ReturnType<typeof getActionType>,
  upgradeAmounts: Record<string, number | null>
): string => {
  switch (actionType) {
    case 'current':
      return 'Plano atual';
    case 'subscribe':
      return planDetail.id === 'free' ? 'Selecionar' : `Assinar por R$${planDetail.price}/mês`;
    case 'upgrade':
      const upgradeAmount = upgradeAmounts[planDetail.id];
      if (upgradeAmount !== undefined && upgradeAmount !== null) {
        return `Upgrade por R$${(Math.abs(upgradeAmount) / 100).toFixed(2)}`;
      }
      return `Upgrade para R$${planDetail.price}/mês`;
    case 'downgrade':
      const downgradeAmount = upgradeAmounts[planDetail.id];
      if (downgradeAmount !== undefined && downgradeAmount !== null) {
        return `Downgrade (crédito R$${(Math.abs(downgradeAmount) / 100).toFixed(2)})`;
      }
      return `Downgrade para R$${planDetail.price}/mês`;
    default:
      return 'Selecionar';
  }
};
