
import React from 'react';
import { Loader2 } from 'lucide-react';

export function AuthLoader() {
  return (
    <div className="container py-8">
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <h2 className="text-xl font-medium">Carregando...</h2>
        <p className="text-muted-foreground mt-2">
          Verificando suas informações de usuário.
        </p>
      </div>
    </div>
  );
}
