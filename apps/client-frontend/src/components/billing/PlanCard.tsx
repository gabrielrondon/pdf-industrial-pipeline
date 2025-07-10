
import { UserPlan, PlanDetails } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Loader2, ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getActionType, getButtonText } from './utils/planUtils';

interface PlanCardProps {
  plan: PlanDetails;
  currentPlan: UserPlan;
  user: any;
  selectedPlan: UserPlan | null;
  upgradeAmounts: Record<string, number | null>;
  isLoadingPlan: boolean;
  isRedirecting: boolean;
  onSelectPlan: (planId: UserPlan) => void;
  onPlanAction: (planId: UserPlan) => void;
}

export function PlanCard({
  plan,
  currentPlan,
  user,
  selectedPlan,
  upgradeAmounts,
  isLoadingPlan,
  isRedirecting,
  onSelectPlan,
  onPlanAction
}: PlanCardProps) {
  const isCurrentPlan = currentPlan === plan.id;
  const isSelected = selectedPlan === plan.id;
  const actionType = getActionType(plan.id, currentPlan, user);

  const getButtonIcon = () => {
    if (actionType === 'upgrade') return <ArrowUp className="h-4 w-4 mr-2" />;
    if (actionType === 'downgrade') return <ArrowDown className="h-4 w-4 mr-2" />;
    return null;
  };

  const formatPrice = (amount: number) => {
    return (amount / 100).toFixed(2);
  };

  return (
    <Card 
      className={cn(
        "relative border-2 transition-all",
        plan.recommended ? "border-secondary shadow-md" : "border-border",
        isCurrentPlan ? "border-primary ring-2 ring-primary ring-opacity-50" : "",
        isSelected ? "ring-2 ring-secondary ring-opacity-70" : ""
      )}
    >
      {plan.recommended && !isCurrentPlan && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-secondary">Recomendado</Badge>
        </div>
      )}
      
      {isCurrentPlan && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-primary">Seu plano atual</Badge>
        </div>
      )}
      
      <CardHeader>
        <CardTitle className="text-2xl">{plan.name}</CardTitle>
        <CardDescription>{plan.description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="text-center">
          <span className="text-4xl font-bold">
            {plan.price > 0 ? `R$${plan.price}` : 'Grátis'}
          </span>
          {plan.price > 0 && (
            <span className="text-muted-foreground">/mês</span>
          )}
          
          {/* Show credit information */}
          <div className="mt-2 p-2 bg-muted/50 rounded-md">
            <div className="text-sm font-medium text-primary">
              {plan.credits.toLocaleString()} créditos/mês
            </div>
            <div className="text-xs text-muted-foreground">
              1 análise = ~10 créditos
            </div>
          </div>
          
          {/* Show proration amount for upgrades/downgrades */}
          {actionType === 'upgrade' && upgradeAmounts[plan.id] !== undefined && upgradeAmounts[plan.id] !== null && (
            <div className="text-sm text-green-600 mt-1">
              Upgrade: +R${formatPrice(Math.abs(upgradeAmounts[plan.id]!))} hoje
            </div>
          )}
          {actionType === 'downgrade' && upgradeAmounts[plan.id] !== undefined && upgradeAmounts[plan.id] !== null && (
            <div className="text-sm text-blue-600 mt-1">
              Crédito: R${formatPrice(Math.abs(upgradeAmounts[plan.id]!))} na próxima fatura
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          {plan.features.map((feature, index) => {
            const isEnabled = feature[plan.id];
            
            return (
              <div 
                key={index} 
                className={cn(
                  "flex items-start",
                  !isEnabled && "text-muted-foreground"
                )}
              >
                <div className="mr-2">
                  {isEnabled ? (
                    <div className="h-5 w-5 rounded-full bg-accent flex items-center justify-center">
                      <Check className="h-3 w-3 text-white" />
                    </div>
                  ) : (
                    <div className="h-5 w-5 rounded-full border border-muted-foreground" />
                  )}
                </div>
                <span className="text-sm">{feature.title}</span>
              </div>
            );
          })}
        </div>
      </CardContent>
      
      <CardFooter>
        <Button 
          className="w-full"
          variant={plan.recommended && !isCurrentPlan ? "default" : "outline"}
          disabled={isLoadingPlan || isRedirecting || actionType === 'current'}
          onClick={() => {
            onSelectPlan(plan.id);
            onPlanAction(plan.id);
          }}
        >
          {isLoadingPlan || isRedirecting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processando...
            </>
          ) : (
            <>
              {getButtonIcon()}
              {getButtonText(plan, actionType, upgradeAmounts)}
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
