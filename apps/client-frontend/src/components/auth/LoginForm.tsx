import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertTriangle } from 'lucide-react';
import { EmailConfirmationHandler } from './EmailConfirmationHandler';

const formSchema = z.object({
  email: z.string().email('Digite um email válido'),
  password: z.string().min(6, 'A senha deve ter no mínimo 6 caracteres'),
});

type FormData = z.infer<typeof formSchema>;

export function LoginForm() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: FormData) => {
    if (isSubmitting) return;

    setIsSubmitting(true);
    setError(null);
    setShowEmailConfirmation(false);
    
    try {
      console.log('🔑 LoginForm: Starting login for', data.email);
      await signIn(data.email, data.password);
      console.log('✅ LoginForm: Login successful, redirecting to dashboard');
      
      // Aguardar um pouco para o estado de auth atualizar
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 100);
      
    } catch (err: any) {
      console.error('❌ LoginForm: Login error:', err);
      
      if (err.name === 'EmailNotConfirmed' || err.message === 'Email not confirmed') {
        setUserEmail(data.email);
        setShowEmailConfirmation(true);
      } else if (err.message?.includes('Invalid login credentials')) {
        setError('Email ou senha incorretos. Verifique seus dados e tente novamente.');
      } else if (err.message?.includes('Too many requests')) {
        setError('Muitas tentativas de login. Aguarde alguns minutos e tente novamente.');
      } else {
        setError('Erro no login. Tente novamente.');
      }
      setIsSubmitting(false);
    }
  };

  if (showEmailConfirmation) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-yellow-500" />
            Confirme seu email
          </CardTitle>
          <CardDescription>
            Você precisa confirmar seu email antes de acessar o Arremate360
          </CardDescription>
        </CardHeader>
        <CardContent>
          <EmailConfirmationHandler 
            email={userEmail}
            onClose={() => {
              setShowEmailConfirmation(false);
              setUserEmail('');
              setError(null);
            }}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Entrar no Arremate360</CardTitle>
        <CardDescription>
          Acesse sua conta para continuar utilizando nossa plataforma
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="seu@email.com" type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Senha</FormLabel>
                  <FormControl>
                    <Input placeholder="••••••••" type="password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex flex-col space-y-2">
        <div className="text-sm text-center">
          <Button variant="link" className="p-0" onClick={() => navigate('/forgot-password')}>
            Esqueceu a senha?
          </Button>
        </div>
        <div className="text-sm text-center">
          Não tem uma conta?{' '}
          <Button variant="link" className="p-0" onClick={() => navigate('/signup')}>
            Cadastre-se no Arremate360
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
