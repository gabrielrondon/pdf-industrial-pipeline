
import React from 'react';
import { useAuth } from '@/contexts/AuthContext';

export function FeaturesSection() {
  const { user } = useAuth();

  return (
    <div className="rounded-lg border p-6 bg-muted/20">
      <h3 className="font-medium text-lg mb-4">Recursos disponíveis</h3>
      <ul className="space-y-2 text-sm text-muted-foreground">
        <li>• <strong>Análise estruturada:</strong> Identificação automática de pontos jurídicos relevantes e riscos.</li>
        <li>• <strong>Busca semântica:</strong> Faça perguntas em linguagem natural e encontre trechos específicos.</li>
        <li>• <strong>Processamento inteligente:</strong> Divisão do documento em blocos com sobreposição para preservar contexto.</li>
        <li>• <strong>IA avançada:</strong> Utiliza embeddings OpenAI para análise semântica precisa.</li>
        {user?.plan === 'free' ? (
          <li className="text-secondary font-medium">
            • No plano gratuito, os leads identificados são automaticamente compartilhados com outros usuários.
          </li>
        ) : (
          <li>
            • Com seu plano {user?.plan === 'premium' ? 'Premium' : 'Pro'}, você pode escolher manter seus leads privados.
          </li>
        )}
      </ul>
    </div>
  );
}
