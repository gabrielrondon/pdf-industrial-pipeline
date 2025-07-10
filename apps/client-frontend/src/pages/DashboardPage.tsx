import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { CreditHistory } from '@/components/credits/CreditHistory';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PlusCircle, FileText, ChevronRight } from 'lucide-react';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { documents } = useDocuments();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const recentDocuments = documents.slice(0, 3);
  
  return (
    <div className="container py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Bem-vindo, {user?.name || 'usuário'}! Veja um resumo de suas atividades.
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Button onClick={() => navigate('/upload')}>
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
        
        {/* Quick upload */}
        <div className="mt-10">
          <Card>
            <CardHeader>
              <CardTitle>Iniciar nova análise</CardTitle>
              <CardDescription>
                Faça upload de um documento para análise automatizada
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                className="w-full py-8 text-lg"
                variant="outline"
                onClick={() => navigate('/upload')}
              >
                <PlusCircle className="h-6 w-6 mr-2" />
                Analisar documento
              </Button>
            </CardContent>
          </Card>
        </div>
        
        {/* Recent documents */}
        <div className="mt-10">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Documentos recentes</h2>
            <Button variant="link" onClick={() => navigate('/documents')}>
              Ver todos
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
          
          {recentDocuments.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-10">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">Nenhum documento analisado ainda</h3>
                <p className="text-muted-foreground text-sm mt-1 mb-4">
                  Faça upload de um documento para começar
                </p>
                <Button onClick={() => navigate('/upload')}>
                  Realizar primeira análise
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {recentDocuments.map((doc) => (
                <Card key={doc.id} className="overflow-hidden">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg truncate" title={doc.fileName}>
                          {doc.fileName}
                        </CardTitle>
                        <CardDescription>
                          {new Date(doc.analyzedAt).toLocaleDateString('pt-BR')}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pb-3">
                    <div className="text-sm text-muted-foreground mb-2">
                      {doc.points.length} pontos identificados
                    </div>
                  </CardContent>
                  <div className="px-6 py-3 bg-muted/20 border-t">
                    <Button variant="link" className="px-0" asChild>
                      <a href={`/documents/${doc.id}`}>
                        Ver detalhes
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </a>
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
        
        {/* Premium features */}
        {user?.plan !== 'premium' && (
          <div className="mt-10">
            <Card className="bg-secondary/5 border-secondary/20">
              <CardHeader>
                <CardTitle>Desbloqueie recursos premium</CardTitle>
                <CardDescription>
                  Aprimore sua experiência com o plano Premium
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-white/80 border">
                    <h3 className="font-medium mb-2">Leads da comunidade</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Acesse leads compartilhados por outros usuários
                    </p>
                    <Button variant="outline" className="w-full" size="sm">
                      Descobrir
                    </Button>
                  </div>
                  
                  <div className="p-4 rounded-lg bg-white/80 border">
                    <h3 className="font-medium mb-2">Controle total de privacidade</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Decida quais leads compartilhar e quais manter privados
                    </p>
                    <Button variant="outline" className="w-full" size="sm">
                      Saiba mais
                    </Button>
                  </div>
                  
                  <div className="p-4 rounded-lg bg-white/80 border">
                    <h3 className="font-medium mb-2">Suporte prioritário</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Obtenha assistência exclusiva para suas necessidades
                    </p>
                    <Button variant="outline" className="w-full" size="sm">
                      Entrar em contato
                    </Button>
                  </div>
                </div>
                
                <div className="mt-6 text-center">
                  <Button onClick={() => navigate('/plans')}>
                    Fazer upgrade para Premium
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
