
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useProcessingJob } from './hooks/useProcessingJob';
import { getStatusIcon, getStatusColor, getStatusText } from './utils/statusUtils';
import { LoadingState } from './components/LoadingState';
import { EmptyState } from './components/EmptyState';
import { ProgressSection } from './components/ProgressSection';
import { StatusAlerts } from './components/StatusAlerts';
import { JobDetails } from './components/JobDetails';

interface ProcessingStatusProps {
  documentId: string;
  onProcessingComplete?: () => void;
}

export function ProcessingStatus({ documentId, onProcessingComplete }: ProcessingStatusProps) {
  const { job, isLoading } = useProcessingJob({ documentId, onProcessingComplete });

  if (isLoading) {
    return <LoadingState />;
  }

  if (!job) {
    return <EmptyState />;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(job.status)}
            <span className="text-lg">Status do Processamento</span>
          </div>
          <Badge className={getStatusColor(job.status)}>
            {getStatusText(job.status)}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <ProgressSection status={job.status} progress={job.progress} />
        <StatusAlerts status={job.status} errorMessage={job.error_message} />
        <JobDetails createdAt={job.created_at} completedAt={job.completed_at} />
      </CardContent>
    </Card>
  );
}
