
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { EmailConfirmationHandler } from '@/components/auth/EmailConfirmationHandler';
import { supabase } from '@/integrations/supabase/client';
import { toast } from '@/components/ui/use-toast';

export default function EmailConfirmationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const handleEmailConfirmation = async () => {
      const token = searchParams.get('token');
      const type = searchParams.get('type');
      const userEmail = searchParams.get('email');
      
      if (userEmail) {
        setEmail(userEmail);
      }

      if (token && type === 'signup') {
        try {
          const { error } = await supabase.auth.verifyOtp({
            token_hash: token,
            type: 'signup'
          });

          if (error) {
            console.error('Error confirming email:', error);
            toast({
              title: "Erro na confirmação",
              description: "Não foi possível confirmar seu email. Tente novamente.",
              variant: "destructive",
            });
          } else {
            toast({
              title: "Email confirmado!",
              description: "Sua conta foi ativada com sucesso. Você pode fazer login agora.",
            });
            navigate('/login');
          }
        } catch (error) {
          console.error('Error during email confirmation:', error);
          toast({
            title: "Erro na confirmação",
            description: "Ocorreu um erro inesperado. Tente novamente.",
            variant: "destructive",
          });
        }
      }
      
      setIsProcessing(false);
    };

    handleEmailConfirmation();
  }, [searchParams, navigate]);

  const handleClose = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <EmailConfirmationHandler 
          email={email || ''} 
          onClose={handleClose}
        />
      </div>
    </div>
  );
}
