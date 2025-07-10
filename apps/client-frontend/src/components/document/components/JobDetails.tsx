
import React from 'react';

interface JobDetailsProps {
  createdAt: string;
  completedAt?: string;
}

export function JobDetails({ createdAt, completedAt }: JobDetailsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
      <div>
        <span className="font-medium">Criado:</span>
        <br />
        {new Date(createdAt).toLocaleString('pt-BR')}
      </div>
      {completedAt && (
        <div>
          <span className="font-medium">Concluído:</span>
          <br />
          {new Date(completedAt).toLocaleString('pt-BR')}
        </div>
      )}
    </div>
  );
}
