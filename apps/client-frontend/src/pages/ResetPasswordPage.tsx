import { useSearchParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [valid, setValid] = useState(false);

  useEffect(() => {
    const type = searchParams.get('type');
    if (type === 'recovery') {
      setValid(true);
    }
  }, [searchParams]);

  if (!valid) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card>
          <CardContent className="space-y-4 p-6">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>Link inválido ou expirado.</AlertDescription>
            </Alert>
            <Button onClick={() => navigate('/login')} className="w-full">
              Voltar ao login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <ResetPasswordForm />
    </div>
  );
}
