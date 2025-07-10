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
import { Loader2 } from 'lucide-react';
import { usePlan } from '@/contexts/PlanContext';
import { UserPlan } from '@/types';
import { EmailConfirmationHandler } from './EmailConfirmationHandler';

const formSchema = z
  .object({
    email: z.string().email('Digite um email válido'),
    password: z.string().min(6, 'A senha deve ter no mínimo 6 caracteres'),
    confirmPassword: z.string().min(6, 'Confirme sua senha'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'As senhas não correspondem',
    path: ['confirmPassword'],
  });

type FormData = z.infer<typeof formSchema>;

interface SignupFormProps {
  selectedPlan?: UserPlan;
}

export function SignupForm({ selectedPlan = 'free' }: SignupFormProps) {
  const { signUp, isAuthenticated } = useAuth();
  const { planDetails } = usePlan();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<UserPlan>(selectedPlan);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const onSubmit = async (data: FormData) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setError(null);
    setShowEmailConfirmation(false);
    
    try {
      await signUp(data.email, data.password, plan);
      
      // Mostrar tela de confirmação de email em vez de navegar
      setUserEmail(data.email);
      setShowEmailConfirmation(true);
    } catch (err: any) {
      console.error('Signup form error:', err);
      setError(err.message || 'Falha no cadastro. Tente novamente mais tarde.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showEmailConfirmation) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Confirme seu email</CardTitle>
          <CardDescription>
            Quase lá! Confirme seu email para ativar sua conta
          </CardDescription>
        </CardHeader>
        <CardContent>
          <EmailConfirmationHandler 
            email={userEmail}
            onClose={() => navigate('/login')}
          />
        </CardContent>
        <CardFooter>
          <Button 
            variant="ghost" 
            className="w-full" 
            onClick={() => navigate('/login')}
          >
            Ir para o login
          </Button>
        </CardFooter>
      </Card>
    );
  }

  const selectedPlanDetails = planDetails.find(p => p.id === plan) || planDetails[0];

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Criar conta</CardTitle>
        <CardDescription>
          Crie sua conta para começar a analisar documentos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
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
            
            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirmar senha</FormLabel>
                  <FormControl>
                    <Input placeholder="••••••••" type="password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="space-y-3 py-2">
              <div className="text-sm font-medium">Escolha seu plano:</div>
              <div className="flex flex-wrap gap-2">
                {planDetails.map((planOption) => (
                  <Button
                    key={planOption.id}
                    type="button"
                    variant={plan === planOption.id ? "default" : "outline"}
                    className={`flex-1 ${plan === planOption.id ? 'bg-secondary' : ''}`}
                    onClick={() => setPlan(planOption.id)}
                    disabled={isSubmitting}
                  >
                    {planOption.name}
                    {planOption.price > 0 && <span className="text-xs ml-1">R${planOption.price}/mês</span>}
                  </Button>
                ))}
              </div>
              <div className="text-xs text-muted-foreground pt-1">
                Plano selecionado: <span className="font-semibold">{selectedPlanDetails.name}</span>
                {selectedPlanDetails.price > 0 ? (
                  <> - R${selectedPlanDetails.price}/mês</>
                ) : (
                  " - Grátis"
                )}
              </div>
            </div>
            
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Cadastrando...
                </>
              ) : (
                'Criar conta'
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex flex-col space-y-2">
        <div className="text-sm text-center">
          Já tem uma conta?{' '}
          <Button variant="link" className="p-0" onClick={() => navigate('/login')}>
            Entrar
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
