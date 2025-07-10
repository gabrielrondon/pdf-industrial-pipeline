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
    <div className="container py-8">
      <h1 className="text-3xl font-bold tracking-tight mb-6">Meu Perfil</h1>
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Informações da Conta</CardTitle>
          <CardDescription>Atualize seus dados de usuário</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Salvar</Button>
            </form>
          </Form>
          <div className="text-sm text-muted-foreground">
            <div className="mt-4">
              <span className="font-medium">Email:</span> {user.email}
            </div>
            <div className="mt-1 capitalize">
              <span className="font-medium">Plano:</span> {user.plan}
            </div>
            {credits !== undefined && (
              <div className="mt-1">
                <span className="font-medium">Créditos disponíveis:</span> {credits}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      <Card className="max-w-md mt-6">
        <CardHeader>
          <CardTitle>Alterar Senha</CardTitle>
          <CardDescription>Defina uma nova senha para sua conta</CardDescription>
        </CardHeader>
        <CardContent>
          <ChangePasswordForm />
        </CardContent>
      </Card>
    </div>
  );
}
