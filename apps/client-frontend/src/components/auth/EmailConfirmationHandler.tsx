import React from 'react'
// NOTE: To personalize the confirmation email, update the template in Supabase Dashboard > Authentication > Templates > Confirm Signup. Add Arremate360 branding and instructions.

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Mail, AlertTriangle, CheckCircle } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';

interface EmailConfirmationHandlerProps {
  email: string;
  onClose: () => void;
}

export function EmailConfirmationHandler({ email, onClose }: EmailConfirmationHandlerProps) {
  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [newEmail, setNewEmail] = useState(email);

  const handleResendConfirmation = async () => {
    setIsResending(true);
    setMessage(null);
    
    try {
      const redirectTo = typeof window !== 'undefined' ? `${window.location.origin}/email-confirmation` : undefined;
      
      const { error } = await supabase.auth.resend({
        type: 'signup',
        email: newEmail,
        options: {
          emailRedirectTo: redirectTo
        }
      });

      if (error) {
        setMessage({ type: 'error', text: 'Erro ao reenviar email. Tente novamente.' });
      } else {
        setMessage({ type: 'success', text: 'Email de confirmação reenviado com sucesso!' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao reenviar email. Tente novamente.' });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-yellow-600 mb-4">
        <Mail className="h-5 w-5" />
        <span className="text-sm font-medium">Email não confirmado</span>
      </div>
      
      <p className="text-sm text-muted-foreground">
        Enviamos um email de confirmação para <strong>{email}</strong>. 
        Verifique sua caixa de entrada e spam, e clique no link para ativar sua conta.
      </p>

      <div className="space-y-3">
        <div>
          <label htmlFor="email" className="text-sm font-medium">
            Reenviar para outro email (opcional):
          </label>
          <Input
            id="email"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            placeholder="seu@email.com"
          />
        </div>

        <Button 
          onClick={handleResendConfirmation} 
          disabled={isResending || !newEmail}
          className="w-full"
          variant="outline"
        >
          {isResending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Reenviando...
            </>
          ) : (
            <>
              <Mail className="mr-2 h-4 w-4" />
              Reenviar email de confirmação
            </>
          )}
        </Button>
      </div>

      {message && (
        <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
          {message.type === 'error' ? (
            <AlertTriangle className="h-4 w-4" />
          ) : (
            <CheckCircle className="h-4 w-4" />
          )}
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      <Button 
        onClick={onClose} 
        variant="ghost" 
        className="w-full"
      >
        Voltar ao login
      </Button>
    </div>
  );
}
