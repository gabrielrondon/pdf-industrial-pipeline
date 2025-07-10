import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, CheckCircle, FileText, ShieldCheck, Users } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-secondary">Arremate</span>
            <span className="text-primary">360</span>
          </h1>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
            Análise automatizada de leilões judiciais
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Faça upload de editais e processos para identificar automaticamente pontos jurídicos relevantes e oportunidades de negócio.
          </p>
          
          {!isAuthenticated && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="text-lg px-8 py-4" onClick={handleGetStarted}>
                Entrar
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4" onClick={() => navigate('/signup')}>
                Cadastrar
              </Button>
              
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg p-8 shadow-lg">
            <FileText className="h-12 w-12 text-primary mb-4" />
            <h3 className="text-xl font-bold mb-4">Upload Inteligente</h3>
            <p className="text-gray-600">
              Carregue editais de leilão e processos judiciais para análise automática por nosso sistema de IA.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-8 shadow-lg">
            <CheckCircle className="h-12 w-12 text-primary mb-4" />
            <h3 className="text-xl font-bold mb-4">Análise Jurídica</h3>
            <p className="text-gray-600">
              Identificação automática de pontos relevantes, riscos e oportunidades em documentos jurídicos.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-8 shadow-lg">
            <Users className="h-12 w-12 text-primary mb-4" />
            <h3 className="text-xl font-bold mb-4">Comunidade</h3>
            <p className="text-gray-600">
              Compartilhe leads de qualidade e acesse oportunidades descobertas por outros usuários.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg p-8 shadow-lg">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">Como funciona?</h3>
              <ul className="space-y-3">
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span>Faça upload do documento (PDF, DOC, etc.)</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span>Nossa IA analisa o conteúdo automaticamente</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span>Receba pontos jurídicos relevantes identificados</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                  <span>Explore oportunidades e compartilhe com a comunidade</span>
                </li>
              </ul>
            </div>
            
            <div className="text-center">
              <ShieldCheck className="h-24 w-24 text-primary mx-auto mb-4" />
              <h4 className="text-lg font-medium">Seguro e Confiável</h4>
              <p className="text-gray-600 text-sm">
                Seus documentos são processados com total segurança e privacidade.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
