import { SignupForm } from '@/components/auth/SignupForm';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronLeft, Crown, Shield, Zap } from 'lucide-react';
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
          Já tem uma conta?{' '}
          <Button 
            variant="link" 
            className="p-0 text-arremate-gold-400 hover:text-arremate-gold-300" 
            onClick={() => navigate('/login')}
          >
            Entrar
          </Button>
        </div>
      </div>
      
      {/* Premium Signup Container */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 relative">
        {/* Background Decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -left-40 w-80 h-80 rounded-full bg-arremate-gold-500/10"></div>
          <div className="absolute -bottom-40 -right-40 w-80 h-80 rounded-full bg-arremate-navy-400/10"></div>
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
            <p className="text-arremate-navy-200 text-lg mb-4">
              Crie sua conta para começar a analisar documentos
            </p>
            
            {/* Plan Badge */}
            {selectedPlan !== 'free' && (
              <div className="bg-arremate-gold-500/20 border border-arremate-gold-400/30 px-4 py-2 rounded-full text-arremate-gold-300 text-sm font-semibold mb-4">
                🏆 Plano {selectedPlan === 'pro' ? 'Pro' : 'Premium'} Selecionado
              </div>
            )}
          </div>
          
          {/* Signup Form Container */}
          <div className="bg-white/95 backdrop-blur-sm p-8 rounded-xl shadow-2xl border border-white/20">
            <SignupForm selectedPlan={selectedPlan} />
          </div>
          
          {/* Benefits */}
          <div className="mt-6 grid grid-cols-3 gap-4 text-center text-arremate-navy-300 text-sm">
            <div className="flex flex-col items-center gap-1">
              <Shield className="h-5 w-5 text-arremate-gold-400" />
              <span>Segurança SSL</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Zap className="h-5 w-5 text-arremate-gold-400" />
              <span>IA Especializada</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Crown className="h-5 w-5 text-arremate-gold-400" />
              <span>Líder do Mercado</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
