
import React from 'react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export function UnauthenticatedState() {
  const navigate = useNavigate();

  return (
    <div className="container py-8">
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <h2 className="text-xl font-medium mb-4">Login necessário</h2>
        <p className="text-muted-foreground mb-6">
          Você precisa estar logado para fazer upload de documentos.
        </p>
        <Button onClick={() => navigate('/login')}>
          Fazer Login
        </Button>
      </div>
    </div>
  );
}
