
import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function UploadHeader() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center gap-2 mb-6">
      <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
        <ChevronLeft className="h-4 w-4 mr-1" />
        <span>Voltar</span>
      </Button>
      <h1 className="text-3xl font-bold tracking-tight">Análise de documento</h1>
    </div>
  );
}
