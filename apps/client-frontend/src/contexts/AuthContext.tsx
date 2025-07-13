import { createContext, useContext, useEffect, useState, ReactNode, useCallback, useRef, useMemo } from 'react';
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
  const initializationRef = useRef(false);


  // Garantir que o componente está hidratado no cliente
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const { data: { user: supabaseUser }, error } = await supabase.auth.getUser();
      if (error || !supabaseUser) {
        setUser(null);
        return;
      }
      const userData = createUserFromSupabase(supabaseUser);
      setUser(userData);
    } catch (error) {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    let mounted = true;

    // Timeout de segurança - se após 5 segundos ainda estiver loading, força parada
    const safetyTimeout = setTimeout(() => {
      if (mounted && !initializationRef.current) {
        initializationRef.current = true;
        setIsLoading(false);
      }
    }, 5000);

    // Função para inicializar o estado de autenticação
    const initializeAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          if (mounted && !initializationRef.current) {
            initializationRef.current = true;
            setUser(null);
            setIsLoading(false);
          }
          return;
        }

        if (session?.user && mounted) {
          const userData = createUserFromSupabase(session.user);
          setUser(userData);
        } else if (mounted) {
          setUser(null);
        }

        if (mounted && !initializationRef.current) {
          initializationRef.current = true;
          setIsLoading(false);
        }
      } catch (error) {
        if (mounted && !initializationRef.current) {
          initializationRef.current = true;
          setUser(null);
          setIsLoading(false);
        }
      }
    };

    // Configurar listener para mudanças de autenticação
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (!mounted) {
          return;
        }

        // Evitar processamento desnecessário se já inicializado e não há mudança real
        if (initializationRef.current && event === 'TOKEN_REFRESHED') {
          return;
        }

        if (session?.user) {
          const userData = createUserFromSupabase(session.user);
          setUser(prev => {
            // Evitar re-render se o usuário não mudou
            if (prev && prev.id === userData.id && prev.email === userData.email) {
              return prev;
            }
            return userData;
          });
        } else {
          setUser(prev => prev === null ? null : null);
        }
      }
    );

    // Inicializar o estado de autenticação
    initializeAuth();

    return () => {
      mounted = false;
      clearTimeout(safetyTimeout);
      subscription.unsubscribe();
    };
  }, [isHydrated]); // Dependência do isHydrated

  const signUp = useCallback(async (email: string, password: string, name?: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name: name || '' }
      }
    });

    if (error) {
      throw error;
    }
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      // Mapear erros específicos
      if (error.message === 'Email not confirmed') {
        const customError = new Error('Email not confirmed');
        customError.name = 'EmailNotConfirmed';
        throw customError;
      }
      throw error;
    }
  }, []);

  const signOut = useCallback(async () => {
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
  }, []);

  const resetPassword = useCallback(async (email: string) => {
    const redirectTo =
      typeof window !== 'undefined' ? `${window.location.origin}/reset-password` : undefined;
    const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo });
    if (error) throw error;
  }, []);

  const updatePassword = useCallback(async (password: string) => {
    const { error } = await supabase.auth.updateUser({ password });
    if (error) throw error;
  }, []);

  const isAuthenticated = !!user;

  const contextValue = useMemo(() => ({
    user,
    isLoading,
    isAuthenticated,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
    refreshUser
  }), [user, isLoading, isAuthenticated, signUp, signIn, signOut, resetPassword, updatePassword, refreshUser]);

  return (
    <AuthContext.Provider value={contextValue}>
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
