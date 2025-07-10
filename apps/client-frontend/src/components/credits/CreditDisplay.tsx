
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Coins, TrendingUp, TrendingDown } from 'lucide-react';

export function CreditDisplay() {
  const { user } = useAuth();

  if (!user) return null;

  const getPlanCredits = (plan: string) => {
    switch (plan) {
      case 'free': return 1000;
      case 'pro': return 5000;
      case 'premium': return 10000;
      default: return 1000;
    }
  };

  const planMaxCredits = getPlanCredits(user.plan);
  const usagePercentage = planMaxCredits > 0 ? ((user.credits_used || 0) / planMaxCredits) * 100 : 0;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Coins className="h-5 w-5 text-yellow-500" />
          Seus Créditos
        </CardTitle>
        <CardDescription>
          Créditos disponíveis para análise de documentos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold text-primary">
            {user.credits || 0}
          </div>
          <Badge variant="outline" className="text-xs">
            {user.plan.toUpperCase()}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Usado este mês</span>
            <span>{user.credits_used || 0} / {planMaxCredits}</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary rounded-full h-2 transition-all"
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
        </div>

        <div className="flex justify-between items-center text-sm">
          <div className="flex items-center gap-1 text-green-600">
            <TrendingUp className="h-3 w-3" />
            <span>Ganhos: {user.credits_earned || 0}</span>
          </div>
          <div className="flex items-center gap-1 text-red-600">
            <TrendingDown className="h-3 w-3" />
            <span>Gastos: {user.credits_used || 0}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
