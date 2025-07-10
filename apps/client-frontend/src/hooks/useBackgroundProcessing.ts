
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { toast } from '@/components/ui/use-toast';

export function useBackgroundProcessing() {
  const { user } = useAuth();

  const startBackgroundProcessing = async (documentId: string, fileUrl: string) => {
    if (!user) return;

    try {
      // Create processing job using direct insert
      const jobData = {
        document_id: documentId,
        user_id: user.id,
        status: 'pending',
        job_type: 'document_analysis',
        progress: 0
      };

      // Use fetch directly to avoid type issues
      const response = await fetch(`https://rjbiyndpxqaallhjmbwm.supabase.co/rest/v1/processing_jobs`, {
        method: 'POST',
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify(jobData)
      });

      if (!response.ok) {
        console.error('Error creating processing job');
        return;
      }

      // Start processing
      const { error: processError } = await supabase.functions.invoke('process-document-chunks', {
        body: { documentId, fileUrl }
      });

      if (processError) {
        console.error('Error starting background processing:', processError);
        toast({
          title: "Aviso",
          description: "A análise básica foi concluída, mas o processamento avançado pode ter falhado.",
          variant: "default",
        });
      } else {
        toast({
          title: "Processamento iniciado",
          description: "O documento está sendo processado para busca semântica em segundo plano.",
        });
      }
    } catch (error) {
      console.error('Error in background processing:', error);
    }
  };

  return { startBackgroundProcessing };
}
