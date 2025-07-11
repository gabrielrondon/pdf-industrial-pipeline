
import React, { useState, useEffect } from 'react';
import { Progress } from '@/components/ui/progress';
import { getProgressText } from '../utils/statusUtils';

interface ProgressSectionProps {
  status: string;
  progress: number;
}

export function ProgressSection({ status, progress }: ProgressSectionProps) {
  const [displayProgress, setDisplayProgress] = useState(progress);
  const [currentMessage, setCurrentMessage] = useState('');

  useEffect(() => {
    // Smooth progress animation
    const smoothProgressUpdate = () => {
      setDisplayProgress(prev => {
        if (prev < progress) {
          // Incrementally increase by 1-2% every 200ms
          const increment = Math.min(Math.random() * 2 + 0.5, progress - prev);
          return Math.min(prev + increment, progress);
        }
        return prev;
      });
    };

    const progressInterval = setInterval(smoothProgressUpdate, 200);
    return () => clearInterval(progressInterval);
  }, [progress]);

  useEffect(() => {
    // Update message every 2-3 seconds
    const updateMessage = () => {
      setCurrentMessage(getProgressText(Math.floor(displayProgress), status));
    };

    updateMessage(); // Initial message
    const messageInterval = setInterval(updateMessage, 2500);
    return () => clearInterval(messageInterval);
  }, [displayProgress, status]);

  if (status !== 'processing' && status !== 'pending') {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm">
        <span className="text-blue-600 font-medium animate-pulse">
          {currentMessage}
        </span>
        <span className="font-mono text-blue-700">
          {Math.floor(displayProgress)}%
        </span>
      </div>
      <Progress value={displayProgress} className="h-3 transition-all duration-300 ease-out" />
      <div className="text-xs text-gray-500 text-center">
        💡 Dica: Enquanto isso, que tal preparar seus documentos para o próximo leilão?
      </div>
    </div>
  );
}
