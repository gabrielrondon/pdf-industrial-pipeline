import { useNavigate } from 'react-router-dom';
import { PlanCards } from '@/components/billing/PlanCards';
import { Button } from '@/components/ui/button';
import { ChevronLeft, CreditCard, RefreshCw } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { usePlan } from '@/contexts/PlanContext';
import { toast } from 'sonner';

export default function PlansPage() {
  const { user } = useAuth();
  const { currentPlan, openCustomerPortal, refreshPlanDetails, isLoadingPlan } = usePlan();
  const navigate = useNavigate();
  
  const handlePortal = async () => {
    try {
      const portalUrl = await openCustomerPortal();
      window.location.href = portalUrl;
    } catch (error) {
      console.error('Failed to open customer portal:', error);
    }
  };

  const handleRefresh = async () => {
    try {
      toast.loading('Verificando status da assinatura...', { id: 'refresh' });
      await refreshPlanDetails();
      toast.dismiss('refresh');
      toast.success('Status da assinatura atualizado!');
    } catch (error) {
      toast.dismiss('refresh');
      toast.error('Erro ao verificar assinatura');
    }
  };
  
  return (
    <div className="container py-8">
      <div className="flex items-center gap-2 mb-6">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          <span>Voltar</span>
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">Planos e assinaturas</h1>
      </div>
      
      <div className="max-w-5xl mx-auto space-y-8">
        {user && (
          <div className="bg-secondary/10 rounded-lg p-6 mb-8 border border-secondary/20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-xl font-semibold">Seu plano atual: {currentPlan === 'free' ? 'Gratuito' : currentPlan === 'pro' ? 'Pro' : 'Premium'}</h2>
                <p className="text-muted-foreground mt-1">
                  {currentPlan === 'free'
                    ? 'Você está usando a versão gratuita com recursos limitados.'
                    : currentPlan === 'pro'
                    ? 'Você tem acesso aos recursos Pro, incluindo privacidade de leads e créditos por compartilhamento.'
                    : 'Você tem acesso a todos os recursos Premium, incluindo leads da comunidade e suporte prioritário.'}
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleRefresh} disabled={isLoadingPlan}>
                  <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingPlan ? 'animate-spin' : ''}`} />
                  Verificar Status
                </Button>
                
                {currentPlan !== 'free' && (
                  <Button variant="outline" onClick={handlePortal} disabled={isLoadingPlan}>
                    <CreditCard className="h-4 w-4 mr-2" />
                    Gerenciar assinatura
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
        
        <div>
          <PlanCards />
        </div>
        
        <div className="bg-muted/30 rounded-lg p-6 mt-12 border">
          <h2 className="text-xl font-semibold mb-4">Perguntas frequentes</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">Como funciona o compartilhamento de leads?</h3>
              <p className="text-sm text-muted-foreground mt-1">
                No plano Gratuito, todos os leads são automaticamente compartilhados com a comunidade. Nos planos Pro e Premium, você decide quais leads compartilhar e quais manter privados.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium">O que são os créditos e como posso usá-los?</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Créditos são pontos ganhos ao compartilhar leads de qualidade. Eles podem ser usados para acessar recursos premium adicionais e análises avançadas.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium">Posso mudar de plano a qualquer momento?</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Sim, você pode fazer upgrade ou downgrade do seu plano a qualquer momento. As mudanças são aplicadas imediatamente e o valor é ajustado proporcionalmente.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium">Como funciona o acesso aos leads da comunidade?</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Usuários Premium têm acesso exclusivo a todos os leads compartilhados pela comunidade, podendo filtrar por tipo de documento, região e outros critérios.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
