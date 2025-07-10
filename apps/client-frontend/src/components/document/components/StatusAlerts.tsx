
import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface StatusAlertsProps {
  status: string;
  errorMessage?: string;
}

export function StatusAlerts({ status, errorMessage }: StatusAlertsProps) {
  if (status === 'completed') {
    return (
      <Alert className="bg-green-50 border-green-200">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          Documento processado com sucesso! Agora você pode usar a busca semântica para encontrar informações específicas.
        </AlertDescription>
      </Alert>
    );
  }

  if (status === 'failed' && errorMessage) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Erro: {errorMessage}
        </AlertDescription>
      </Alert>
    );
  }

  return null;
}
