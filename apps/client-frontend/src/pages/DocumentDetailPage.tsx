import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocuments } from '@/contexts/DocumentContext';
import { AnalysisResult } from '@/components/document/AnalysisResult';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Save, FileText, Clock, Calendar, NotebookPen, Eye } from 'lucide-react';
import { DocumentAnalysis } from '@/types';

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { documents, isLoading } = useDocuments();
  const [document, setDocument] = useState<DocumentAnalysis | null>(null);
  const [notes, setNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    if (documents.length > 0 && id) {
      const foundDoc = documents.find(doc => doc.id === id);
      if (foundDoc) {
        setDocument(foundDoc);
        // Load saved notes from localStorage
        const savedNotes = localStorage.getItem(`document_notes_${id}`);
        if (savedNotes) {
          setNotes(savedNotes);
        }
      }
    }
  }, [documents, id]);

  const handleSaveNotes = async () => {
    if (!id) return;
    
    setIsSaving(true);
    try {
      // Save notes to localStorage (in a real app, this would be saved to the backend)
      localStorage.setItem(`document_notes_${id}`, notes);
      setSaveMessage('Anotações salvas com sucesso! ✅');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Erro ao salvar anotações ❌');
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="container py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-16 w-16 text-muted-foreground mb-4" />
            <h2 className="text-xl font-medium mb-2">Documento não encontrado</h2>
            <p className="text-muted-foreground text-center max-w-md mb-6">
              O documento que você está procurando não existe ou foi removido.
            </p>
            <Button onClick={() => navigate('/documents')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar aos documentos
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            onClick={() => navigate('/documents')}
            className="shrink-0"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{document.fileName}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">
                {document.type === 'edital' ? 'Edital de Leilão' : 
                 document.type === 'processo' ? 'Processo Judicial' :
                 document.type === 'laudo' ? 'Laudo Técnico' : 'Outro Documento'}
              </Badge>
              <span className="text-sm text-muted-foreground flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                {formatDate(document.analyzedAt)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Document Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total de Leads</p>
                <p className="text-2xl font-bold">{document.points.length}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Leads Confirmados</p>
                <p className="text-2xl font-bold text-green-600">
                  {document.points.filter(p => p.status === 'confirmado').length}
                </p>
              </div>
              <Eye className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Alertas</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {document.points.filter(p => p.status === 'alerta').length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Notes Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <NotebookPen className="h-5 w-5" />
            Minhas Anotações
          </CardTitle>
          <CardDescription>
            Adicione suas observações, estratégias e lembrete sobre este documento
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Escreva suas anotações aqui... 

Algumas ideias:
• Estratégia de lance
• Pontos de atenção 
• Contatos importantes
• Prazos críticos
• Análise de viabilidade"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="min-h-32 resize-none"
          />
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">
              {notes.length} caracteres
            </span>
            <div className="flex gap-2 items-center">
              {saveMessage && (
                <span className="text-sm text-green-600">{saveMessage}</span>
              )}
              <Button 
                onClick={handleSaveNotes} 
                disabled={isSaving}
                size="sm"
              >
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? 'Salvando...' : 'Salvar Anotações'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      <AnalysisResult analysis={document} />
    </div>
  );
}