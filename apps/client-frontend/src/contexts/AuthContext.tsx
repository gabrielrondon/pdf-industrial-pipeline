import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User as SupabaseUser } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';
import { User } from '@/types';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signUp: (email: string, password: string, name?: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (password: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Função auxiliar para criar um usuário padrão sem buscar no banco
const createUserFromSupabase = (supabaseUser: SupabaseUser): User => {
  console.log('🏗️ Creating user from Supabase data only');
  return {
    id: supabaseUser.id,
    email: supabaseUser.email || '',
    name: supabaseUser.user_metadata?.name || '',
    plan: 'free', // Default plan
    credits: 100, // Default credits
    credits_used: 0,
    credits_earned: 0,
    createdAt: supabaseUser.created_at || new Date().toISOString()
  };
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isHydrated, setIsHydrated] = useState(false);

  console.log('🔄 AuthProvider render - isLoading:', isLoading, 'user:', user?.email, 'isHydrated:', isHydrated);

  // Garantir que o componente está hidratado no cliente
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const refreshUser = async () => {
    console.log('🔄 refreshUser called');
    try {
      const { data: { user: supabaseUser }, error } = await supabase.auth.getUser();
      if (error || !supabaseUser) {
        console.log('❌ refreshUser: no user or error:', error);
        setUser(null);
        return;
      }
      console.log('✅ refreshUser: user found, creating simple user...');
      const userData = createUserFromSupabase(supabaseUser);
      setUser(userData);
      console.log('✅ refreshUser: user set:', userData.email);
    } catch (error) {
      console.error('❌ Error refreshing user:', error);
      setUser(null);
    }
  };

  useEffect(() => {
    if (!isHydrated) {
      console.log('⏳ Waiting for hydration...');
      return;
    }

    console.log('🚀 AuthProvider useEffect starting');
    let mounted = true;

    // Timeout de segurança - se após 5 segundos ainda estiver loading, força parada
    const safetyTimeout = setTimeout(() => {
      if (mounted && isLoading) {
        console.log('⏰ Safety timeout reached - forcing loading to false');
        setIsLoading(false);
      }
    }, 5000);

    // Função para inicializar o estado de autenticação
    const initializeAuth = async () => {
      console.log('🔄 initializeAuth starting');
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        console.log('📱 getSession result:', { 
          hasSession: !!session, 
          hasUser: !!session?.user,
          userEmail: session?.user?.email,
          error: error?.message,
          sessionDetails: session ? {
            accessToken: session.access_token ? 'exists' : 'missing',
            refreshToken: session.refresh_token ? 'exists' : 'missing',
            expiresAt: session.expires_at,
            expiresIn: session.expires_in
          } : null
        });
        
        // Verificar se há dados no localStorage apenas no cliente
        if (typeof window !== 'undefined') {
          const localStorageKeys = [];
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.includes('supabase')) {
              localStorageKeys.push(key);
            }
          }
          console.log('🗄️ Supabase localStorage keys:', localStorageKeys);
        }
        
        if (error) {
          console.error('❌ Error getting session:', error);
          if (mounted) {
            setUser(null);
            setIsLoading(false);
            console.log('✅ Loading set to false (error case)');
          }
          return;
        }

        if (session?.user && mounted) {
          console.log('👤 Session user found, creating simple user...');
          const userData = createUserFromSupabase(session.user);
          setUser(userData);
          console.log('✅ User set from session:', userData.email);
        } else if (mounted) {
          console.log('❌ No session user');
          setUser(null);
        }

        if (mounted) {
          setIsLoading(false);
          console.log('✅ Loading set to false (normal case)');
        }
      } catch (error) {
        console.error('❌ Error initializing auth:', error);
        if (mounted) {
          setUser(null);
          setIsLoading(false);
          console.log('✅ Loading set to false (catch case)');
        }
      }
    };

    // Configurar listener para mudanças de autenticação
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('🔔 Auth state changed:', event, 'hasUser:', !!session?.user, 'userEmail:', session?.user?.email);
        
        if (!mounted) {
          console.log('⚠️ Component unmounted, ignoring auth change');
          return;
        }

        if (session?.user) {
          console.log('👤 Auth change: user found, creating simple user...');
          const userData = createUserFromSupabase(session.user);
          setUser(userData);
          console.log('✅ User set from auth change:', userData.email);
        } else {
          console.log('❌ Auth change: no user');
          setUser(null);
        }
      }
    );

    // Inicializar o estado de autenticação
    initializeAuth();

    return () => {
      console.log('🧹 AuthProvider cleanup');
      mounted = false;
      clearTimeout(safetyTimeout);
      subscription.unsubscribe();
    };
  }, [isHydrated]); // Dependência do isHydrated

  const signUp = async (email: string, password: string, name?: string) => {
    console.log('📝 signUp called for:', email);
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name: name || '' }
      }
    });

    if (error) {
      console.error('❌ signUp error:', error);
      throw error;
    }
    console.log('✅ signUp successful');
  };

  const signIn = async (email: string, password: string) => {
    console.log('🔑 signIn called for:', email);
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      console.error('❌ signIn error:', error);
      // Mapear erros específicos
      if (error.message === 'Email not confirmed') {
        const customError = new Error('Email not confirmed');
        customError.name = 'EmailNotConfirmed';
        throw customError;
      }
      throw error;
    }
    console.log('✅ signIn successful');
  };

  const signOut = async () => {
    console.log('🚪 signOut called');
    // Sign out from Supabase and broadcast to all tabs
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    
    // Limpar estado local
    setUser(null);
    
    // Limpar storage apenas no cliente
    if (typeof window !== 'undefined') {
      localStorage.clear();
      sessionStorage.clear();
    }
    
    // Redirecionar para home sem adicionar entrada ao histórico
    window.location.replace('/');
  };

  const resetPassword = async (email: string) => {
    const redirectTo =
      typeof window !== 'undefined' ? `${window.location.origin}/reset-password` : undefined;
    const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
    if (error) throw error;
  };

  const updatePassword = async (password: string) => {
    const { error } = await supabase.auth.updateUser({ password });
    if (error) throw error;
  };

  const isAuthenticated = !!user;
  console.log('🔍 AuthProvider state:', { isLoading, isAuthenticated, userEmail: user?.email, isHydrated });

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated,
      signUp,
      signIn,
      signOut,
      resetPassword,
      updatePassword,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
