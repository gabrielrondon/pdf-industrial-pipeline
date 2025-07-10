
import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';

export const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'failed':
      return <AlertCircle className="h-5 w-5 text-red-500" />;
    case 'processing':
      return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
    default:
      return <Clock className="h-5 w-5 text-yellow-500" />;
  }
};

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'processing':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-yellow-100 text-yellow-800';
  }
};

export const getStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return 'Aguardando processamento';
    case 'processing':
      return 'Processando documento';
    case 'completed':
      return 'Processamento concluído';
    case 'failed':
      return 'Falha no processamento';
    default:
      return 'Status desconhecido';
  }
};

export const getProgressText = (progress: number, status: string) => {
  if (status === 'completed') return 'Documento processado com sucesso!';
  if (status === 'failed') return 'Erro durante o processamento';
  if (progress <= 10) return 'Preparando para processamento...';
  if (progress <= 30) return 'Baixando e validando arquivo...';
  if (progress <= 50) return 'Extraindo texto das páginas...';
  if (progress <= 70) return 'Dividindo texto em blocos...';
  if (progress <= 90) return 'Gerando representações vetoriais...';
  return 'Finalizando processamento...';
};
