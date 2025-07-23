import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  ChevronDown, 
  ChevronRight, 
  ExternalLink, 
  Eye,
  BookOpen,
  Building2,
  DollarSign,
  Calendar,
  Phone,
  FileText,
  AlertTriangle,
  TrendingUp,
  Clock,
  MapPin,
  User,
  Mail,
  Home,
  Car,
  Store
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PremiumLeadCardProps {
  lead: {
    id: string;
    title: string;
    comment: string;
    status: string;
    category: string;
    priority: string;
    page_reference?: number;
    details?: Record<string, any>;
    raw_value?: string;
    value?: string;
  };
  isExpanded: boolean;
  onToggleExpanded: () => void;
  onViewPage?: (pageNum: number) => void;
}

export function PremiumLeadCard({ lead, isExpanded, onToggleExpanded, onViewPage }: PremiumLeadCardProps) {
  const hasDetails = lead.details || lead.page_reference || lead.raw_value;

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'leilao':
        return <Building2 className="h-4 w-4" />;
      case 'investimento':
        return <TrendingUp className="h-4 w-4" />;
      case 'prazo':
        return <Calendar className="h-4 w-4" />;
      case 'financeiro':
        return <DollarSign className="h-4 w-4" />;
      case 'contato':
        return <Phone className="h-4 w-4" />;
      case 'geral':
        return <FileText className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getPropertyIcon = (title: string) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('apartamento')) return <Building2 className="h-4 w-4" />;
    if (titleLower.includes('casa')) return <Home className="h-4 w-4" />;
    if (titleLower.includes('comercial')) return <Store className="h-4 w-4" />;
    if (titleLower.includes('veículo') || titleLower.includes('carro')) return <Car className="h-4 w-4" />;
    return <MapPin className="h-4 w-4" />;
  };

  const getPriorityStyles = (priority: string) => {
    switch (priority) {
      case 'high':
        return {
          border: 'border-l-red-500',
          bg: 'bg-red-50',
          accent: 'bg-red-100 text-red-800 border-red-200'
        };
      case 'medium':
        return {
          border: 'border-l-arremate-gold-500',
          bg: 'bg-arremate-gold-50',
          accent: 'bg-arremate-gold-100 text-arremate-gold-800 border-arremate-gold-200'
        };
      case 'low':
        return {
          border: 'border-l-green-500',
          bg: 'bg-green-50',
          accent: 'bg-green-100 text-green-800 border-green-200'
        };
      default:
        return {
          border: 'border-l-arremate-charcoal-300',
          bg: 'bg-arremate-charcoal-50',
          accent: 'bg-arremate-charcoal-100 text-arremate-charcoal-800 border-arremate-charcoal-200'
        };
    }
  };

  const getCategoryStyles = (category: string) => {
    switch (category) {
      case 'leilao':
        return 'bg-arremate-navy-100 text-arremate-navy-800 border-arremate-navy-200';
      case 'investimento':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'financeiro':
        return 'bg-arremate-gold-100 text-arremate-gold-800 border-arremate-gold-200';
      case 'prazo':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'contato':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-arremate-charcoal-100 text-arremate-charcoal-800 border-arremate-charcoal-200';
    }
  };

  const priorityStyles = getPriorityStyles(lead.priority);

  return (
    <Collapsible open={isExpanded} onOpenChange={onToggleExpanded}>
      <CollapsibleTrigger asChild>
        <Card 
          className={cn(
            "cursor-pointer transition-all duration-200 hover:shadow-md border-l-4",
            priorityStyles.border,
            priorityStyles.bg,
            "hover:shadow-arremate-navy-200/20"
          )}
        >
          <CardContent className="p-4">
            <div className="flex justify-between items-start">
              <div className="font-semibold flex items-center gap-3 text-arremate-charcoal-900">
                <div className="flex items-center gap-2">
                  {lead.category === 'investimento' ? getPropertyIcon(lead.title) : getCategoryIcon(lead.category)}
                  <span className="text-base">{lead.title}</span>
                </div>
                
                {lead.value && (
                  <Badge variant="outline" className="bg-arremate-gold-50 text-arremate-gold-800 border-arremate-gold-300 font-semibold">
                    {lead.value}
                  </Badge>
                )}
                
                {lead.page_reference && (
                  <Badge variant="outline" className="bg-arremate-navy-50 text-arremate-navy-700 border-arremate-navy-200">
                    <BookOpen className="h-3 w-3 mr-1" />
                    Pág. {lead.page_reference}
                  </Badge>
                )}
              </div>
              
              <div className="flex gap-2 items-center">
                <Badge variant="outline" className={getCategoryStyles(lead.category)}>
                  {lead.category}
                </Badge>
                
                <Badge variant="outline" className={priorityStyles.accent}>
                  {lead.priority}
                </Badge>
                
                {hasDetails && (
                  <div className="h-6 w-6 flex items-center justify-center">
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-arremate-charcoal-600" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-arremate-charcoal-600" />
                    )}
                  </div>
                )}
              </div>
            </div>
            
            <p className="mt-3 text-sm text-arremate-charcoal-700 leading-relaxed">
              {lead.comment}
            </p>
          </CardContent>
        </Card>
      </CollapsibleTrigger>
      
      {hasDetails && (
        <CollapsibleContent className="mt-3">
          <div className="bg-white border border-arremate-charcoal-200 rounded-lg shadow-sm">
            <div className="bg-arremate-navy-50 px-4 py-3 border-b border-arremate-charcoal-200 rounded-t-lg">
              <h5 className="font-semibold text-sm text-arremate-navy-800 flex items-center">
                <Eye className="h-4 w-4 mr-2" />
                Detalhes Específicos
              </h5>
            </div>
            
            <div className="p-4 space-y-4">
              {lead.page_reference && (
                <div className="bg-arremate-navy-50 p-4 rounded-lg border border-arremate-navy-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-arremate-navy-800 flex items-center">
                      <BookOpen className="h-4 w-4 mr-1" />
                      Localização no Documento
                    </span>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onViewPage && lead.page_reference) {
                          onViewPage(lead.page_reference);
                        }
                      }}
                      className="h-8 text-xs bg-arremate-navy-100 hover:bg-arremate-navy-200 border-arremate-navy-300 text-arremate-navy-800"
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Ver Página {lead.page_reference}
                    </Button>
                  </div>
                  <span className="text-xs text-arremate-navy-600">
                    Esta informação foi encontrada na página {lead.page_reference} do documento original
                  </span>
                </div>
              )}
              
              {lead.details && (
                <div className="bg-arremate-charcoal-50 p-4 rounded-lg border border-arremate-charcoal-200">
                  <h6 className="font-semibold text-xs text-arremate-charcoal-700 mb-3 uppercase tracking-wide">
                    Informações Técnicas
                  </h6>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(lead.details).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-arremate-gold-500 rounded-full flex-shrink-0"></div>
                        <span className="text-sm text-arremate-charcoal-600 capitalize font-medium">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-sm font-semibold text-arremate-charcoal-900">
                          {String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {lead.raw_value && (
                <div className="bg-gradient-to-r from-arremate-gold-50 to-arremate-gold-100 p-4 rounded-lg border border-arremate-gold-200">
                  <div className="text-xs font-semibold text-arremate-gold-800 mb-2 flex items-center">
                    <FileText className="h-3 w-3 mr-1" />
                    TEXTO ORIGINAL
                  </div>
                  <blockquote className="text-sm text-arremate-gold-700 italic leading-relaxed border-l-2 border-arremate-gold-400 pl-3">
                    "{lead.raw_value}"
                  </blockquote>
                </div>
              )}
            </div>
          </div>
        </CollapsibleContent>
      )}
    </Collapsible>
  );
}