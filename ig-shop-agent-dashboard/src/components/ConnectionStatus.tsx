import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';
import { apiService, checkApiConnection } from '../services/api';

interface ConnectionStatusProps {
  className?: string;
}

export function ConnectionStatus({ className }: ConnectionStatusProps) {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [apiInfo, setApiInfo] = useState<any>(null);

  const testConnection = async () => {
    setIsLoading(true);
    try {
      // Test basic connection
      const connected = await checkApiConnection();
      setIsConnected(connected);
      
      if (connected) {
        // Get API info if connected
        const healthResponse = await apiService.healthCheck();
        if (healthResponse.data) {
          setApiInfo(healthResponse.data);
        }
      }
      
      setLastChecked(new Date());
    } catch (error) {
      setIsConnected(false);
      console.error('Connection test failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Test connection on mount
  useEffect(() => {
    testConnection();
  }, []);

  const getStatusDisplay = () => {
    if (isLoading) {
      return {
        icon: <Clock className="w-4 h-4" />,
        text: 'Testing...',
        variant: 'secondary' as const,
        color: 'text-yellow-600'
      };
    }
    
    if (isConnected === true) {
      return {
        icon: <CheckCircle className="w-4 h-4" />,
        text: 'Connected',
        variant: 'default' as const,
        color: 'text-green-600'
      };
    }
    
    if (isConnected === false) {
      return {
        icon: <XCircle className="w-4 h-4" />,
        text: 'Disconnected',
        variant: 'destructive' as const,
        color: 'text-red-600'
      };
    }
    
    return {
      icon: <Clock className="w-4 h-4" />,
      text: 'Unknown',
      variant: 'secondary' as const,
      color: 'text-gray-600'
    };
  };

  const status = getStatusDisplay();

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center justify-between">
          Backend API Status
          <Button
            variant="outline"
            size="sm"
            onClick={testConnection}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Test Connection
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Connection Status:</span>
          <Badge variant={status.variant} className="flex items-center gap-1">
            <span className={status.color}>{status.icon}</span>
            {status.text}
          </Badge>
        </div>
        
        {lastChecked && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500">Last Checked:</span>
            <span className="text-slate-700">
              {lastChecked.toLocaleTimeString()}
            </span>
          </div>
        )}
        
        {apiInfo && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">API Version:</span>
              <span className="text-slate-700">{apiInfo.version}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Status:</span>
              <span className="text-slate-700 capitalize">{apiInfo.status}</span>
            </div>
          </div>
        )}
        
        <div className="pt-2 border-t">
          <div className="text-xs text-slate-500">
            <strong>API Endpoint:</strong><br />
            https://igshop-api.azurewebsites.net
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 