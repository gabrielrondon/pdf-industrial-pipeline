
import React from 'react';
import { Progress } from '@/components/ui/progress';
import { getProgressText } from '../utils/statusUtils';

interface ProgressSectionProps {
  status: string;
  progress: number;
}

export function ProgressSection({ status, progress }: ProgressSectionProps) {
  if (status !== 'processing' && status !== 'pending') {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span>{getProgressText(progress, status)}</span>
        <span>{progress}%</span>
      </div>
      <Progress value={progress} className="h-2" />
    </div>
  );
}
