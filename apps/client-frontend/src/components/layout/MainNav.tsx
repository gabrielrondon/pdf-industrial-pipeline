import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  BarChart, 
  FileText, 
  Home, 
  LogOut, 
  Search, 
  Settings, 
  Upload, 
  User, 
  Users 
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

export function MainNav() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get user initials for avatar
  const getInitials = (name?: string) => {
    if (!name) return 'U';
    
    const names = name.split(' ');
    if (names.length === 1) return name.charAt(0).toUpperCase();
    
    return `${names[0].charAt(0)}${names[names.length - 1].charAt(0)}`.toUpperCase();
  };
  
  const navItems = [
    {
      label: 'Dashboard',
      href: '/dashboard',
      icon: Home,
      needsAuth: true,
    },
    {
      label: 'Análise',
      href: '/upload',
      icon: Upload,
      needsAuth: true,
    },
    {
      label: 'Documentos',
      href: '/documents',
      icon: FileText,
      needsAuth: true,
    },
    {
      label: 'Estatísticas',
      href: '/stats',
      icon: BarChart,
      needsAuth: true,
    },
    {
      label: 'Leads da Comunidade',
      href: '/community',
      icon: Users,
      needsAuth: true,
      premiumOnly: true,
    },
  ];
  
  const handleLogout = async () => {
    try {
      await signOut()
      // Navigation is handled by window.location.replace in signOut
    } catch (err) {
      // Optionally show a toast or alert
      alert('Erro ao sair. Tente novamente.')
    }
  };
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  return (
    <header className="sticky top-0 z-30 w-full border-b bg-background">
      <div className="container flex h-16 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold">
              <span className="text-secondary">Arremate</span>
              <span className="text-primary">360</span>
            </span>
          </Link>
        </div>
        
        <div className="flex-1">
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              // Don't show items that need auth if user is not logged in
              if (item.needsAuth && !user) return null;
              
              // Don't show premium-only items for non-premium users
              if (item.premiumOnly && user?.plan !== 'premium') return null;
              
              return (
                <Button
                  key={item.href}
                  variant={isActive(item.href) ? 'default' : 'ghost'}
                  className={cn('flex gap-1 items-center', isActive(item.href) ? 'bg-secondary text-secondary-foreground' : '')}
                  asChild
                >
                  <Link to={item.href}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                </Button>
              );
            })}
          </nav>
        </div>
        
        <div className="flex items-center space-x-2">
          {user ? (
            <>
              {user.plan !== 'free' && (
                <Badge variant="outline" className="bg-accent/20 border-accent text-accent-foreground">
                  {user.plan === 'premium' ? 'Premium' : 'Pro'}
                </Badge>
              )}
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-secondary text-secondary-foreground">
                        {getInitials(user.name)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Minha conta</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/profile')}>
                    <User className="mr-2 h-4 w-4" />
                    <span>Perfil</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/plans')}>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Gerenciar assinatura</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Sair</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              <Button variant="ghost" onClick={() => navigate('/login')}>
                Entrar
              </Button>
              <Button onClick={() => navigate('/signup')}>
                Cadastrar
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
