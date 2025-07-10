
import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

export type AIModel = 'native' | 'openai' | 'mistral' | 'anthropic';

interface ModelSelectorProps {
  value: AIModel;
  onValueChange: (value: AIModel) => void;
  disabled?: boolean;
}

export function ModelSelector({ value, onValueChange, disabled }: ModelSelectorProps) {
  const models = [
    {
      id: 'native' as AIModel,
      name: 'Análise Nativa',
      description: 'Análise rápida sem IA - Gratuito',
      badge: 'Grátis',
      badgeVariant: 'default' as const
    },
    {
      id: 'openai' as AIModel,
      name: 'OpenAI GPT-4o',
      description: 'Mais versátil e completo',
      badge: 'Popular',
      badgeVariant: 'secondary' as const
    },
    {
      id: 'mistral' as AIModel,
      name: 'Mistral Large',
      description: 'Rápido e eficiente',
      badge: 'Rápido',
      badgeVariant: 'secondary' as const
    },
    {
      id: 'anthropic' as AIModel,
      name: 'Claude Sonnet',
      description: 'Excelente para análise jurídica',
      badge: 'Jurídico',
      badgeVariant: 'outline' as const
    }
  ];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Tipo de análise</label>
      <Select value={value} onValueChange={onValueChange} disabled={disabled}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Selecione o tipo de análise" />
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={model.id} value={model.id}>
              <div className="flex items-center justify-between w-full">
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{model.name}</span>
                    <Badge variant={model.badgeVariant} className="text-xs">
                      {model.badge}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">{model.description}</span>
                </div>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
