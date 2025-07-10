import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <div className="container flex justify-between items-center h-16">
        <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          <span>Voltar</span>
        </Button>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold">
              <span className="text-secondary">Arremate</span>
              <span className="text-primary">360</span>
            </h1>
            <p className="text-muted-foreground mt-2">
              Informe seu email para receber o link de recuperação
            </p>
          </div>
          <ForgotPasswordForm />
        </div>
      </div>
    </div>
  );
}
