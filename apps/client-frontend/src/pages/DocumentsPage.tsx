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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <div className="flex items-center gap-2">
          <Files className="h-6 w-6 text-muted-foreground" />
          <h1 className="text-3xl font-bold tracking-tight">Meus documentos</h1>
        </div>
        <div className="mt-4 sm:mt-0">
          <Button onClick={() => navigate('/upload')}>
            <PlusCircle className="h-4 w-4 mr-2" />
            Nova análise
          </Button>
        </div>
      </div>
      
      {documents.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Files className="h-16 w-16 text-muted-foreground mb-4" />
            <h2 className="text-xl font-medium mb-2">Nenhum documento analisado</h2>
            <p className="text-muted-foreground text-center max-w-md mb-6">
              Você ainda não analisou nenhum documento. Comece fazendo upload de um edital de leilão ou processo judicial.
            </p>
            <Button onClick={() => navigate('/upload')}>
              <PlusCircle className="h-4 w-4 mr-2" />
              Analisar primeiro documento
            </Button>
          </CardContent>
        </Card>
      ) : (
        <DocumentList />
      )}
    </div>
  );
}
