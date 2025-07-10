import { SignupForm } from '@/components/auth/SignupForm';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';
import { UserPlan } from '@/types';
import { useAuth } from '@/contexts/AuthContext';

export default function SignupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isLoading } = useAuth();
  const selectedPlan = (location.state as { selectedPlan?: UserPlan })?.selectedPlan || 'free';
  
  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="text-xl font-medium">Carregando...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="container flex justify-between items-center h-16">
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          <span>Voltar</span>
        </Button>
        <div className="text-sm">
          Já tem uma conta?{' '}
          <Button variant="link" className="p-0" onClick={() => navigate('/login')}>
            Entrar
          </Button>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold">
              <span className="text-secondary">Arremate</span>
              <span className="text-primary">360</span>
            </h1>
            <p className="text-muted-foreground mt-2">
              Crie sua conta para começar a analisar documentos
            </p>
          </div>
          
          <SignupForm selectedPlan={selectedPlan} />
        </div>
      </div>
    </div>
  );
}
