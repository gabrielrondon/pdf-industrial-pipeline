import { LoginForm } from '@/components/auth/LoginForm';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Navigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  // Mostrar loading enquanto verifica autenticação
  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="text-xl font-medium animate-pulse">Carregando...</div>
      </div>
    );
  }

  // Se já autenticado, redirecionar para dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      <div className="container flex justify-between items-center h-16">
        <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          <span>Voltar</span>
        </Button>
        <div className="text-sm">
          Não tem uma conta?{' '}
          <Button variant="link" className="p-0" onClick={() => navigate('/signup')}>
            Cadastre-se
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
              Entre em sua conta para acessar a plataforma
            </p>
          </div>
          
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
