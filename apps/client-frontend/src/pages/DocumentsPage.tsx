import { useDocuments } from '@/contexts/DocumentContext';
import { DocumentList } from '@/components/document/DocumentList';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { PlusCircle, Files } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DocumentsPage() {
  const { documents } = useDocuments();
  const navigate = useNavigate();
  
  return (
    <div className="container py-8">
      {/* Premium Header */}
      <div className="bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 p-8 rounded-xl border border-arremate-navy-800 shadow-lg mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div className="flex items-center gap-4">
            <div className="bg-arremate-gold-500 p-3 rounded-lg">
              <Files className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Meus Documentos</h1>
              <p className="text-arremate-navy-200 mt-1">
                {documents.length > 0 
                  ? `${documents.length} documento${documents.length !== 1 ? 's' : ''} analisado${documents.length !== 1 ? 's' : ''}`
                  : 'Seus documentos analisados aparecerão aqui'
                }
              </p>
            </div>
          </div>
          <div className="mt-4 sm:mt-0">
            <Button 
              onClick={() => navigate('/upload')}
              className="bg-arremate-gold-500 hover:bg-arremate-gold-600 text-arremate-gold-900 font-semibold px-6 py-2 shadow-lg"
            >
              <PlusCircle className="h-4 w-4 mr-2" />
              Nova Análise
            </Button>
          </div>
        </div>
      </div>
      
      {documents.length === 0 ? (
        <div className="bg-gradient-to-r from-arremate-charcoal-50 to-arremate-charcoal-100 p-12 rounded-xl border border-arremate-charcoal-200 text-center">
          <div className="bg-arremate-navy-100 p-6 rounded-full w-fit mx-auto mb-6">
            <Files className="h-16 w-16 text-arremate-navy-600" />
          </div>
          <h2 className="text-2xl font-bold text-arremate-charcoal-900 mb-3">Nenhum documento analisado</h2>
          <p className="text-arremate-charcoal-600 text-center max-w-2xl mx-auto mb-8 leading-relaxed">
            Você ainda não analisou nenhum documento. Comece fazendo upload de um edital de leilão ou processo judicial e descubra oportunidades valiosas com nossa IA especializada.
          </p>
          <div className="space-y-4">
            <Button 
              onClick={() => navigate('/upload')}
              size="lg"
              className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-8 py-3 shadow-lg"
            >
              <PlusCircle className="h-5 w-5 mr-2" />
              Analisar Primeiro Documento
            </Button>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto mt-8">
              <div className="bg-white p-4 rounded-lg border border-arremate-charcoal-200 shadow-sm">
                <div className="text-arremate-navy-600 font-semibold mb-1">📊 Análise IA</div>
                <div className="text-sm text-arremate-charcoal-600">Identificação automática de leads</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-arremate-charcoal-200 shadow-sm">
                <div className="text-arremate-gold-600 font-semibold mb-1">⚖️ Conformidade</div>
                <div className="text-sm text-arremate-charcoal-600">Verificação legal CPC Art. 889</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-arremate-charcoal-200 shadow-sm">
                <div className="text-green-600 font-semibold mb-1">💰 Oportunidades</div>
                <div className="text-sm text-arremate-charcoal-600">Avaliação de potencial de investimento</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <DocumentList />
      )}
    </div>
  );
}
