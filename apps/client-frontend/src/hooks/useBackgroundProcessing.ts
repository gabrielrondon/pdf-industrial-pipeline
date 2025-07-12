
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { toast } from '@/components/ui/use-toast';

export function useBackgroundProcessing() {
  const { user } = useAuth();

  const startBackgroundProcessing = async (documentId: string, fileUrl: string) => {
    if (!user) return;

    // DEPRECATED: Background processing now happens automatically in Railway API
    // The Railway API handles all document processing during upload
    // This function is kept for compatibility but does nothing
    
    console.log('🚂 Background processing handled by Railway API - no action needed');
    
    // Optional: Show a toast to inform the user
    toast({
      title: "Processamento em andamento",
      description: "O documento está sendo processado automaticamente pela Railway API.",
    });
  };

  return { startBackgroundProcessing };
}
