import { useAuth } from '@/contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import HomePage from './HomePage';

const Index = () => {
  const { isAuthenticated, isLoading } = useAuth();

  console.log('🏠 Index page - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  // Mostrar loading enquanto verifica autenticação
  if (isLoading) {
    console.log('⏳ Index: showing loading screen');
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="text-xl font-medium animate-pulse">Carregando...</div>
      </div>
    );
  }

  // Se autenticado, redirecionar para dashboard
  if (isAuthenticated) {
    console.log('✅ Index: user authenticated, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }
  
  // Se não autenticado, mostrar HomePage
  console.log('❌ Index: user not authenticated, showing HomePage');
  return <HomePage />;
};

export default Index;
