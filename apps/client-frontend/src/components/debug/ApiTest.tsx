/**
 * Componente para testar conectividade com nossa API Railway
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, RefreshCw, Zap } from 'lucide-react';
import { railwayApi } from '@/services/railwayApiService';

interface ApiStatus {
  health: boolean;
  database: boolean;
  redis: boolean;
  environment: string;
  error?: string;
}

interface ApiTestProps {
  compact?: boolean;
}

export function ApiTest({ compact = false }: ApiTestProps) {
  const [status, setStatus] = useState<ApiStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const testApi = async () => {
    setIsLoading(true);
    setStatus(null);

    try {
      // Test health endpoint
      const healthData = await railwayApi.healthCheck();
      console.log('Health check:', healthData);

      setStatus({
        health: healthData.status === 'healthy' || healthData.status === 'degraded',
        database: healthData.services?.database === 'connected' || false,
        redis: healthData.services?.redis === 'connected' || false,
        environment: 'production',
      });

    } catch (error: any) {
      console.error('API Test Error:', error);
      setStatus({
        health: false,
        database: false,
        redis: false,
        environment: 'error',
        error: error.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    testApi();
  }, []);

  const getStatusIcon = (isOk: boolean) => {
    return isOk ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    );
  };

  const getStatusColor = (isOk: boolean) => {
    return isOk ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  // Versão compacta - apenas uma linha com status
  if (compact) {
    return (
      <div className="inline-flex items-center gap-1">
        {isLoading ? (
          <>
            <RefreshCw className="h-3 w-3 animate-spin" />
            <span>Testando...</span>
          </>
        ) : status ? (
          <>
            {status.health ? (
              <CheckCircle className="h-3 w-3 text-green-500" />
            ) : (
              <XCircle className="h-3 w-3 text-red-500" />
            )}
            <span className={status.health ? 'text-green-600' : 'text-red-600'}>
              {status.health ? 'Online' : 'Offline'}
            </span>
          </>
        ) : (
          <span className="text-gray-500">Carregando...</span>
        )}
      </div>
    );
  }

  // Versão completa (existente)
  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Status da API Railway
        </CardTitle>
        <CardDescription>
          Conectividade com nossa API de produção
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-4">
            <RefreshCw className="h-6 w-6 animate-spin text-blue-500" />
            <span className="ml-2">Testando...</span>
          </div>
        ) : status ? (
          <div className="space-y-3">
            {/* Health Status */}
            <div className="flex items-center justify-between">
              <span>API Health</span>
              <div className="flex items-center gap-2">
                {getStatusIcon(status.health)}
                <Badge className={getStatusColor(status.health)}>
                  {status.health ? 'OK' : 'Erro'}
                </Badge>
              </div>
            </div>

            {/* Database Status */}
            <div className="flex items-center justify-between">
              <span>Database</span>
              <div className="flex items-center gap-2">
                {getStatusIcon(status.database)}
                <Badge className={getStatusColor(status.database)}>
                  {status.database ? 'Conectado' : 'Não configurado'}
                </Badge>
              </div>
            </div>

            {/* Redis Status */}
            <div className="flex items-center justify-between">
              <span>Redis</span>
              <div className="flex items-center gap-2">
                {getStatusIcon(status.redis)}
                <Badge className={getStatusColor(status.redis)}>
                  {status.redis ? 'Conectado' : 'Não configurado'}
                </Badge>
              </div>
            </div>

            {/* Environment */}
            <div className="flex items-center justify-between">
              <span>Environment</span>
              <Badge variant="outline">
                {status.environment}
              </Badge>
            </div>

            {/* Error */}
            {status.error && (
              <Alert variant="destructive">
                <AlertDescription>
                  {status.error}
                </AlertDescription>
              </Alert>
            )}

            {/* Warning if database not configured */}
            {status.health && !status.database && (
              <Alert>
                <AlertDescription>
                  ⚠️ API funcionando mas sem database configurado. 
                  Upload de arquivos pode não funcionar corretamente.
                </AlertDescription>
              </Alert>
            )}
          </div>
        ) : null}

        <Button 
          onClick={testApi} 
          disabled={isLoading}
          variant="outline"
          className="w-full"
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Testando...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Testar Novamente
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}