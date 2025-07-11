
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

// Mensagens divertidas estilo Discord para aliviar a ansiedade do usuário
const funnyMessages = [
  'Arremate360 está trabalhando... 🔍',
  'Mais um pouco, ok? ⏰',
  'Analisando cada vírgula... 📋',
  'Procurando as melhores oportunidades... 💎',
  'Quase terminando... prometo! 🤞',
  'Descobrindo tesouros escondidos... 🏆',
  'Verificando se vale a pena... 💰',
  'Mais alguns segundos... ☕',
  'Garimpando informações valiosas... ⛏️',
  'Paciência, estamos quase lá! 🚀',
  'Processando com amor e carinho... ❤️',
  'Conectando os pontos... 🔗',
  'Fazendo a mágica acontecer... ✨',
  'Checando os detalhes importantes... 🔎',
  'Quase pronto para te surpreender! 🎉'
];

let messageIndex = 0;

export const getProgressText = (progress: number, status: string) => {
  if (status === 'completed') return 'Documento processado com sucesso! 🎯';
  if (status === 'failed') return 'Ops! Algo deu errado... 😅';
  
  // Cycle through funny messages
  const message = funnyMessages[messageIndex % funnyMessages.length];
  messageIndex++;
  
  if (progress <= 15) return message;
  if (progress <= 35) return message;
  if (progress <= 55) return message;
  if (progress <= 75) return message;
  if (progress <= 95) return message;
  return 'Últimos ajustes... quase pronto! 🏁';
};
