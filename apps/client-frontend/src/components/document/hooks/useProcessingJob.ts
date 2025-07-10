
import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';

interface ProcessingJob {
  id: string;
  document_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

interface UseProcessingJobProps {
  documentId: string;
  onProcessingComplete?: () => void;
}

export function useProcessingJob({ documentId, onProcessingComplete }: UseProcessingJobProps) {
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchJobStatus = async () => {
    try {
      const response = await fetch(`https://rjbiyndpxqaallhjmbwm.supabase.co/rest/v1/processing_jobs?document_id=eq.${documentId}&order=created_at.desc&limit=1`, {
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data && data.length > 0) {
          setJob(data[0] as ProcessingJob);
        }
      } else {
        console.error('Error fetching job status:', response.status);
      }
    } catch (error) {
      console.error('Error fetching job status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobStatus();
    
    // Set up real-time subscription
    const subscription = supabase
      .channel('job-updates')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'processing_jobs',
          filter: `document_id=eq.${documentId}`
        },
        (payload) => {
          console.log('Job update received:', payload);
          setJob(payload.new as ProcessingJob);
          
          if (payload.new.status === 'completed') {
            onProcessingComplete?.();
          }
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [documentId, onProcessingComplete]);

  return { job, isLoading };
}
