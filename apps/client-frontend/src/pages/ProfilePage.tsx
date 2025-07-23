import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/contexts/DocumentContext';
import { SupabaseService } from '@/services/supabaseService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { ChangePasswordForm } from '@/components/auth/ChangePasswordForm';
import { User, Mail, Crown, CreditCard } from 'lucide-react';

const formSchema = z.object({
  name: z.string().min(2, 'Informe seu nome')
});

type FormData = z.infer<typeof formSchema>;

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const { getStats } = useDocuments();
  const [credits, setCredits] = useState<number>();
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: '' }
  });

  useEffect(() => {
    if (user?.name) {
      form.setValue('name', user.name);
    }
  }, [user?.name, form]);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const stats = await getStats();
        setCredits(stats.credits);
      } catch (err) {
        console.error('Error loading credits:', err);
      }
    };
    if (user) loadStats();
  }, [user, getStats]);

  if (!user) return null;

  const onSubmit = async (data: FormData) => {
    try {
      await SupabaseService.updateUserProfile(user.id, data.name);
      await refreshUser();
      toast.success('Perfil atualizado');
    } catch (err) {
      console.error(err);
      toast.error('Erro ao atualizar perfil');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-arremate-navy-50 to-arremate-charcoal-50">
      <div className="container py-8">
        {/* Premium Profile Header */}
        <div className="bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 p-8 rounded-xl border border-arremate-navy-800 shadow-lg mb-8">
          <div className="flex items-center gap-6">
            <div className="bg-arremate-gold-500 p-4 rounded-full">
              <User className="h-12 w-12 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Meu Perfil</h1>
              <p className="text-arremate-navy-200 mt-1">
                Gerencie suas informações de conta e preferências
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Account Information Card */}
          <div className="bg-white p-8 rounded-xl border border-arremate-charcoal-200 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-arremate-navy-100 p-2 rounded-lg">
                <User className="h-6 w-6 text-arremate-navy-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-arremate-charcoal-900">Informações da Conta</h2>
                <p className="text-arremate-charcoal-600 text-sm">Atualize seus dados de usuário</p>
              </div>
            </div>
            
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-arremate-charcoal-700 font-semibold">Nome</FormLabel>
                      <FormControl>
                        <Input 
                          {...field} 
                          className="border-arremate-charcoal-200 focus:border-arremate-gold-500 focus:ring-arremate-gold-500"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button 
                  type="submit"
                  className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-6 py-2"
                >
                  Salvar Alterações
                </Button>
              </form>
            </Form>
            
            {/* Account Details */}
            <div className="space-y-4 mt-8 pt-6 border-t border-arremate-charcoal-200">
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-arremate-charcoal-500" />
                <div>
                  <span className="font-semibold text-arremate-charcoal-700">Email:</span>
                  <span className="ml-2 text-arremate-charcoal-600">{user.email}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Crown className="h-5 w-5 text-arremate-gold-500" />
                <div>
                  <span className="font-semibold text-arremate-charcoal-700">Plano:</span>
                  <span className="ml-2 text-arremate-charcoal-600 capitalize">{user.plan}</span>
                </div>
              </div>
              {credits !== undefined && (
                <div className="flex items-center gap-3">
                  <CreditCard className="h-5 w-5 text-arremate-navy-500" />
                  <div>
                    <span className="font-semibold text-arremate-charcoal-700">Créditos disponíveis:</span>
                    <span className="ml-2 text-arremate-charcoal-600 font-bold">{credits}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Change Password Card */}
          <div className="bg-white p-8 rounded-xl border border-arremate-charcoal-200 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-arremate-gold-100 p-2 rounded-lg">
                <svg className="h-6 w-6 text-arremate-gold-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-arremate-charcoal-900">Alterar Senha</h2>
                <p className="text-arremate-charcoal-600 text-sm">Defina uma nova senha para sua conta</p>
              </div>
            </div>
            <ChangePasswordForm />
          </div>
        </div>
      </div>
    </div>
  );
}
