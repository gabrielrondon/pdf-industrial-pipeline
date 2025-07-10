import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  console.log('🔒 ProtectedRoute - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  // Mostrar loading enquanto verifica autenticação
  if (isLoading) {
    console.log('⏳ ProtectedRoute: showing loading screen');
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="text-xl font-medium animate-pulse">Carregando...</div>
      </div>
    );
  }

  // Se não autenticado, redirecionar para login
  if (!isAuthenticated) {
    console.log('❌ ProtectedRoute: user not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  // Se autenticado, renderizar o conteúdo
  console.log('✅ ProtectedRoute: user authenticated, rendering children');
  return <>{children}</>;
} 