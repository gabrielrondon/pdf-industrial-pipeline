import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { CreditHistory } from '@/components/credits/CreditHistory';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PlusCircle, FileText, ChevronRight, Users, TrendingUp } from 'lucide-react';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { documents } = useDocuments();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const recentDocuments = (documents || []).slice(0, 3);
  
  return (
    <div className="container py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-arremate-charcoal-900">Dashboard</h1>
          <p className="text-arremate-charcoal-600 mt-1">
            Bem-vindo, {user?.name || 'usuário'}! Veja um resumo de suas atividades.
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Button 
            onClick={() => navigate('/upload')}
            className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-6 py-2 shadow-lg"
          >
            <PlusCircle className="h-4 w-4 mr-2" />
            Nova análise
          </Button>
        </div>
      </div>
      
      <div className="space-y-8">
        {/* Main stats */}
        <DashboardStats />
        
        {/* Credit History */}
        <CreditHistory />
        
        {/* Premium Quick upload */}
        <div className="mt-10">
          <div className="bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 p-8 rounded-xl border border-arremate-navy-800 shadow-lg">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white mb-2">Iniciar nova análise</h3>
              <p className="text-arremate-navy-200 mb-6">
                Faça upload de um documento para análise automatizada
              </p>
              <Button 
                className="bg-arremate-gold-500 hover:bg-arremate-gold-600 text-arremate-gold-900 font-semibold py-4 px-8 text-lg shadow-lg"
                onClick={() => navigate('/upload')}
              >
                <PlusCircle className="h-6 w-6 mr-2" />
                Analisar documento
              </Button>
            </div>
          </div>
        </div>
        
        {/* Premium Recent documents */}
        <div className="mt-10">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-arremate-charcoal-900">Documentos recentes</h2>
            <Button 
              variant="link" 
              onClick={() => navigate('/documents')}
              className="text-arremate-navy-600 hover:text-arremate-navy-700 font-semibold"
            >
              Ver todos
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
          
          {recentDocuments.length === 0 ? (
            <div className="bg-gradient-to-r from-arremate-charcoal-50 to-arremate-charcoal-100 p-12 rounded-xl border border-arremate-charcoal-200 text-center">
              <div className="bg-arremate-navy-100 p-4 rounded-full w-fit mx-auto mb-6">
                <FileText className="h-12 w-12 text-arremate-navy-600" />
              </div>
              <h3 className="text-xl font-semibold text-arremate-charcoal-900 mb-2">Nenhum documento analisado ainda</h3>
              <p className="text-arremate-charcoal-600 text-sm mb-6">
                Faça upload de um documento para começar
              </p>
              <Button 
                onClick={() => navigate('/upload')}
                className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-6 py-2"
              >
                Realizar primeira análise
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {(recentDocuments || []).map((doc) => (
                <div key={doc.id} className="bg-white p-6 rounded-xl border border-arremate-charcoal-200 shadow-sm hover:shadow-md transition-all group">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-arremate-navy-100 p-2 rounded-lg">
                      <FileText className="h-5 w-5 text-arremate-navy-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-arremate-charcoal-900 truncate" title={doc.fileName}>
                        {doc.fileName}
                      </h3>
                      <p className="text-xs text-arremate-charcoal-600">
                        {new Date(doc.analyzedAt).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex items-center gap-2">
                      <div className="bg-arremate-gold-100 px-2 py-1 rounded-full">
                        <span className="text-xs font-semibold text-arremate-gold-800">
                          {doc.points.length} leads
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-arremate-charcoal-100">
                    <Button 
                      variant="ghost" 
                      className="w-full justify-between p-0 h-auto text-arremate-navy-600 hover:text-arremate-navy-700 font-semibold group-hover:bg-arremate-navy-50"
                      asChild
                    >
                      <a href={`/documents/${doc.id}`} className="flex items-center justify-between w-full py-2 px-3 rounded">
                        Ver detalhes
                        <ChevronRight className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Premium features upgrade section */}
        {user?.plan !== 'premium' && (
          <div className="mt-10">
            <div className="bg-gradient-to-r from-arremate-gold-50 to-arremate-gold-100 p-8 rounded-xl border border-arremate-gold-200 shadow-lg">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-arremate-gold-900 mb-2">Desbloqueie recursos premium</h2>
                <p className="text-arremate-gold-700">
                  Aprimore sua experiência com o plano Premium
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl border border-arremate-gold-200 shadow-sm">
                  <div className="bg-arremate-navy-100 p-3 rounded-lg w-fit mb-4">
                    <Users className="h-6 w-6 text-arremate-navy-600" />
                  </div>
                  <h3 className="font-semibold text-arremate-charcoal-900 mb-2">Leads da comunidade</h3>
                  <p className="text-sm text-arremate-charcoal-600 mb-4">
                    Acesse leads compartilhados por outros usuários
                  </p>
                  <Button 
                    variant="outline" 
                    className="w-full border-arremate-navy-300 text-arremate-navy-700 hover:bg-arremate-navy-50" 
                    size="sm"
                  >
                    Descobrir
                  </Button>
                </div>
                
                <div className="bg-white p-6 rounded-xl border border-arremate-gold-200 shadow-sm">
                  <div className="bg-arremate-gold-100 p-3 rounded-lg w-fit mb-4">
                    <FileText className="h-6 w-6 text-arremate-gold-600" />
                  </div>
                  <h3 className="font-semibold text-arremate-charcoal-900 mb-2">Controle total de privacidade</h3>
                  <p className="text-sm text-arremate-charcoal-600 mb-4">
                    Decida quais leads compartilhar e quais manter privados
                  </p>
                  <Button 
                    variant="outline" 
                    className="w-full border-arremate-navy-300 text-arremate-navy-700 hover:bg-arremate-navy-50" 
                    size="sm"
                  >
                    Saiba mais
                  </Button>
                </div>
                
                <div className="bg-white p-6 rounded-xl border border-arremate-gold-200 shadow-sm">
                  <div className="bg-green-100 p-3 rounded-lg w-fit mb-4">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-arremate-charcoal-900 mb-2">Suporte prioritário</h3>
                  <p className="text-sm text-arremate-charcoal-600 mb-4">
                    Obtenha assistência exclusiva para suas necessidades
                  </p>
                  <Button 
                    variant="outline" 
                    className="w-full border-arremate-navy-300 text-arremate-navy-700 hover:bg-arremate-navy-50" 
                    size="sm"
                  >
                    Entrar em contato
                  </Button>
                </div>
              </div>
              
              <div className="text-center">
                <Button 
                  onClick={() => navigate('/plans')}
                  className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-8 py-3 text-lg shadow-lg"
                >
                  Fazer upgrade para Premium
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
