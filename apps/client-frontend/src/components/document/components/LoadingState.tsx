
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export function LoadingState() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Verificando status...</span>
        </div>
      </CardContent>
    </Card>
  );
}
