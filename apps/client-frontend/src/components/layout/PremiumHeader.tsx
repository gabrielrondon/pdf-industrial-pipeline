import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  TrendingUp, 
  Award, 
  Bell, 
  Settings, 
  User,
  LogOut,
  Crown
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';

interface PremiumHeaderProps {
  totalAnalyses?: number;
  className?: string;
}

export function PremiumHeader({ totalAnalyses = 0, className }: PremiumHeaderProps) {
  const { user, signOut } = useAuth();

  return (
    <header className={cn(
      "bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 border-b border-arremate-navy-800 shadow-lg",
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e Brand */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-arremate-gold-500 p-2 rounded-lg shadow-sm">
                <Crown className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  Arremate<span className="text-arremate-gold-400">360</span>
                </h1>
                <p className="text-xs text-arremate-navy-200">
                  Análise Inteligente de Leilões
                </p>
              </div>
            </div>

            {/* Separator */}
            <div className="h-8 w-px bg-arremate-navy-500 mx-2" />

            {/* Stats */}
            <div className="hidden md:flex items-center gap-4">
              <div className="flex items-center gap-2 bg-arremate-navy-500/50 px-3 py-1 rounded-full">
                <FileText className="h-4 w-4 text-arremate-gold-400" />
                <span className="text-sm font-semibold text-white">
                  {totalAnalyses} análises
                </span>
              </div>

              <Badge className="bg-arremate-gold-500 text-arremate-gold-900 border-arremate-gold-400">
                <Award className="h-3 w-3 mr-1" />
                Premium
              </Badge>
            </div>
          </div>

          {/* User Actions */}
          <div className="flex items-center gap-3">
            {/* Notifications */}
            <Button
              variant="ghost"
              size="sm"
              className="text-arremate-navy-200 hover:text-white hover:bg-arremate-navy-500"
            >
              <Bell className="h-4 w-4" />
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              className="text-arremate-navy-200 hover:text-white hover:bg-arremate-navy-500"
            >
              <Settings className="h-4 w-4" />
            </Button>

            {/* User Menu */}
            <div className="flex items-center gap-3 bg-arremate-navy-500/50 px-3 py-2 rounded-full">
              <div className="bg-arremate-gold-500 p-1 rounded-full">
                <User className="h-4 w-4 text-white" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-white">
                  {user?.name || user?.email?.split('@')[0] || 'Usuário'}
                </p>
                <p className="text-xs text-arremate-navy-200">
                  {user?.plan === 'free' ? 'Plano Gratuito' : 'Plano Premium'}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => signOut()}
                className="text-arremate-navy-200 hover:text-white hover:bg-arremate-navy-600 p-1"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Stats */}
      <div className="md:hidden bg-arremate-navy-700 px-4 py-2 border-t border-arremate-navy-600">
        <div className="flex items-center justify-center gap-4">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-arremate-gold-400" />
            <span className="text-sm font-semibold text-white">
              {totalAnalyses} análises
            </span>
          </div>
          <Badge className="bg-arremate-gold-500 text-arremate-gold-900 border-arremate-gold-400">
            <Award className="h-3 w-3 mr-1" />
            Premium
          </Badge>
        </div>
      </div>
    </header>
  );
}