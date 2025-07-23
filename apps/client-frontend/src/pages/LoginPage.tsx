import { LoginForm } from '@/components/auth/LoginForm';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronLeft, Crown } from 'lucide-react';
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
    <div className="min-h-screen bg-gradient-to-br from-arremate-navy-600 via-arremate-navy-700 to-arremate-charcoal-900">
      {/* Premium Navigation */}
      <div className="container flex justify-between items-center h-16 relative z-10">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => navigate('/')}
          className="text-white hover:bg-white/10"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          <span>Voltar</span>
        </Button>
        <div className="text-sm text-arremate-navy-200">
          Não tem uma conta?{' '}
          <Button 
            variant="link" 
            className="p-0 text-arremate-gold-400 hover:text-arremate-gold-300" 
            onClick={() => navigate('/signup')}
          >
            Cadastre-se
          </Button>
        </div>
      </div>
      
      {/* Premium Login Container */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 relative">
        {/* Background Decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-arremate-gold-500/10"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-arremate-navy-400/10"></div>
        </div>
        
        <div className="w-full max-w-md relative z-10">
          {/* Premium Brand Header */}
          <div className="text-center mb-8">
            <div className="bg-arremate-gold-500 p-4 rounded-full w-fit mx-auto mb-6">
              <Crown className="h-12 w-12 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Arremate<span className="text-arremate-gold-400">360</span>
            </h1>
            <p className="text-arremate-navy-200 text-lg">
              Entre em sua conta para acessar a plataforma
            </p>
            <div className="mt-4 text-sm text-arremate-navy-300">
              🏆 Plataforma líder em análise de leilões judiciais
            </div>
          </div>
          
          {/* Login Form Container */}
          <div className="bg-white/95 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-white/20">
            <LoginForm />
          </div>
          
          {/* Trust Indicators */}
          <div className="mt-6 text-center text-arremate-navy-300 text-sm">
            <div className="flex items-center justify-center gap-4">
              <span className="flex items-center gap-1">
                🔒 Segurança SSL
              </span>
              <span className="flex items-center gap-1">
                🏦 Dados Protegidos
              </span>
              <span className="flex items-center gap-1">
                ⚡ IA Especializada
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
