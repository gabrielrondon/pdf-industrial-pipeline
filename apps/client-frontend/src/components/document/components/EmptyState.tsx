
import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText } from 'lucide-react';

export function EmptyState() {
  return (
    <Alert>
      <FileText className="h-4 w-4" />
      <AlertDescription>
        Este documento ainda não foi processado para busca semântica.
      </AlertDescription>
    </Alert>
  );
}
