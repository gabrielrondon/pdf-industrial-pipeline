import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, CheckCircle, FileText, ShieldCheck, Users, Crown, Zap, Award, Star } from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-arremate-navy-600 via-arremate-navy-700 to-arremate-charcoal-900">
      {/* Premium Hero Section */}
      <div className="container mx-auto px-4 py-16 relative">
        {/* Background Decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-20 -right-20 w-96 h-96 rounded-full bg-arremate-gold-500/10"></div>
          <div className="absolute -bottom-20 -left-20 w-96 h-96 rounded-full bg-arremate-navy-400/10"></div>
        </div>
        
        <div className="text-center mb-16 relative z-10">
          {/* Premium Brand */}
          <div className="bg-arremate-gold-500 p-6 rounded-full w-fit mx-auto mb-8">
            <Crown className="h-16 w-16 text-white" />
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold mb-6">
            <span className="text-white">Arremate</span>
            <span className="text-arremate-gold-400">360</span>
          </h1>
          
          <div className="bg-arremate-gold-500/20 border border-arremate-gold-400/30 px-6 py-2 rounded-full w-fit mx-auto mb-6">
            <span className="text-arremate-gold-300 font-semibold flex items-center gap-2">
              <Star className="h-4 w-4" />
              Plataforma Líder em Análise de Leilões Judiciais
            </span>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Análise Inteligente de Documentos Judiciais
          </h2>
          <p className="text-xl text-arremate-navy-200 mb-12 max-w-4xl mx-auto leading-relaxed">
            Transforme editais e processos em oportunidades de investimento com nossa IA especializada em documentação brasileira. Identificação automática de leads, conformidade legal e avaliação de riscos.
          </p>
          
          {!isAuthenticated && (
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Button 
                size="lg" 
                className="text-xl px-12 py-4 bg-arremate-gold-500 hover:bg-arremate-gold-600 text-arremate-gold-900 font-bold shadow-2xl transform hover:scale-105 transition-all" 
                onClick={handleGetStarted}
              >
                Entrar na Plataforma
                <ArrowRight className="ml-3 h-6 w-6" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="text-xl px-12 py-4 border-2 border-white text-white hover:bg-white hover:text-arremate-navy-700 font-semibold" 
                onClick={() => navigate('/signup')}
              >
                Criar Conta Gratuita
              </Button>
            </div>
          )}
          
          {/* Trust Indicators */}
          <div className="mt-12 flex flex-wrap justify-center gap-8 text-arremate-navy-300">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-arremate-gold-400" />
              <span className="text-sm font-medium">Conformidade CPC Art. 889</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-arremate-gold-400" />
              <span className="text-sm font-medium">IA Especializada</span>
            </div>
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-arremate-gold-400" />
              <span className="text-sm font-medium">Líder do Mercado</span>
            </div>
          </div>
        </div>

        {/* Premium Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mb-16 relative z-10">
          <div className="bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-white/20 hover:scale-105 transition-all">
            <div className="bg-arremate-navy-100 p-4 rounded-lg w-fit mb-6">
              <FileText className="h-12 w-12 text-arremate-navy-600" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-arremate-charcoal-900">Upload Inteligente</h3>
            <p className="text-arremate-charcoal-600 leading-relaxed">
              Carregue editais de leilão e processos judiciais para análise automática por nossa IA especializada em documentação brasileira.
            </p>
            <div className="mt-4 text-sm text-arremate-navy-600 font-medium">
              📄 Suporte a PDFs de até 200MB
            </div>
          </div>
          
          <div className="bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-white/20 hover:scale-105 transition-all">
            <div className="bg-arremate-gold-100 p-4 rounded-lg w-fit mb-6">
              <CheckCircle className="h-12 w-12 text-arremate-gold-600" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-arremate-charcoal-900">Análise Jurídica IA</h3>
            <p className="text-arremate-charcoal-600 leading-relaxed">
              Identificação automática de pontos relevantes, conformidade legal CPC Art. 889, riscos e oportunidades de investimento.
            </p>
            <div className="mt-4 text-sm text-arremate-gold-700 font-medium">
              ⚖️ Conformidade automática garantida
            </div>
          </div>
          
          <div className="bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-2xl border border-white/20 hover:scale-105 transition-all">
            <div className="bg-green-100 p-4 rounded-lg w-fit mb-6">
              <Users className="h-12 w-12 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-arremate-charcoal-900">Comunidade Premium</h3>
            <p className="text-arremate-charcoal-600 leading-relaxed">
              Compartilhe leads de qualidade e acesse oportunidades descobertas por outros investidores especializados.
            </p>
            <div className="mt-4 text-sm text-green-600 font-medium">
              🌐 Rede de investidores ativos
            </div>
          </div>
        </div>

        {/* Premium How It Works Section */}
        <div className="bg-white/95 backdrop-blur-sm rounded-xl p-10 shadow-2xl border border-white/20 relative z-10">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-3xl font-bold mb-8 text-arremate-charcoal-900">Como Funciona?</h3>
              <ul className="space-y-6">
                <li className="flex items-start gap-4">
                  <div className="bg-green-100 p-2 rounded-lg flex-shrink-0">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-arremate-charcoal-900">Upload Seguro</div>
                    <div className="text-arremate-charcoal-600">Faça upload do documento PDF com criptografia SSL</div>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="bg-arremate-gold-100 p-2 rounded-lg flex-shrink-0">
                    <Zap className="h-6 w-6 text-arremate-gold-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-arremate-charcoal-900">IA Especializada</div>
                    <div className="text-arremate-charcoal-600">Análise automática com IA treinada em documentação brasileira</div>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="bg-arremate-navy-100 p-2 rounded-lg flex-shrink-0">
                    <Award className="h-6 w-6 text-arremate-navy-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-arremate-charcoal-900">Results Inteligentes</div>
                    <div className="text-arremate-charcoal-600">Leads qualificados, conformidade legal e avaliação de riscos</div>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="bg-purple-100 p-2 rounded-lg flex-shrink-0">
                    <Users className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-arremate-charcoal-900">Comunidade Premium</div>
                    <div className="text-arremate-charcoal-600">Compartilhe oportunidades com investidores especializados</div>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="text-center">
              <div className="bg-arremate-navy-600 p-8 rounded-full w-fit mx-auto mb-6">
                <ShieldCheck className="h-24 w-24 text-white" />
              </div>
              <h4 className="text-2xl font-bold mb-4 text-arremate-charcoal-900">Segurança Premium</h4>
              <p className="text-arremate-charcoal-600 leading-relaxed mb-6">
                Seus documentos são processados com criptografia AES-256, conformidade LGPD e total privacidade garantida.
              </p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-arremate-charcoal-50 p-3 rounded-lg">
                  <div className="font-semibold text-arremate-charcoal-900">🔒 SSL/TLS</div>
                  <div className="text-arremate-charcoal-600">Criptografia</div>
                </div>
                <div className="bg-arremate-charcoal-50 p-3 rounded-lg">
                  <div className="font-semibold text-arremate-charcoal-900">🏦 LGPD</div>
                  <div className="text-arremate-charcoal-600">Conformidade</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
