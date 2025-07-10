
import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { MainNav } from './MainNav';

interface AppLayoutProps {
  children: ReactNode;
  requireAuth?: boolean;
  premiumOnly?: boolean;
}

export function AppLayout({ 
  children, 
  requireAuth = true,
  premiumOnly = false
}: AppLayoutProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="animate-pulse text-center">
          <div className="text-xl font-medium">Carregando...</div>
        </div>
      </div>
    );
  }
  
  // Redirect to login if auth is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  // Redirect to dashboard if premium-only and user is not premium
  if (premiumOnly && user?.plan !== 'premium') {
    return <Navigate to="/plans" />;
  }
  
  return (
    <div className="flex min-h-screen flex-col">
      <MainNav />
      <main className="flex-1">
        {children}
      </main>
      <footer className="py-6 border-t">
        <div className="container flex flex-col sm:flex-row justify-between items-center">
          <div className="text-sm text-muted-foreground mb-2 sm:mb-0">
            &copy; 2025 Arremate360. Todos os direitos reservados.
          </div>
          <div className="flex space-x-4 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground">Termos</a>
            <a href="#" className="hover:text-foreground">Privacidade</a>
            <a href="#" className="hover:text-foreground">Suporte</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
