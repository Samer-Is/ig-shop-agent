import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  MessageCircle, 
  ShoppingCart, 
  DollarSign, 
  TrendingUp, 
  Users, 
  Clock,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { realApiService, useApiConnection, BackendAnalytics, BackendProduct } from '../services/apiService';

interface DashboardData {
  health: any;
  products: BackendProduct[];
  analytics: BackendAnalytics;
  recentMessages: any[];
  instagramStatus: any;
}

export function FunctionalDashboard() {
  const { isConnected, isLoading: connectionLoading } = useApiConnection();
  const [data, setData] = useState<Partial<DashboardData>>({});
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const loadDashboardData = async () => {
    setLoading(true);
    setErrors({});
    
    try {
      // Load all data in parallel
      const [healthRes, productsRes, analyticsRes, messagesRes, instagramRes] = await Promise.allSettled([
        realApiService.healthCheck(),
        realApiService.getProducts(),
        realApiService.getAnalytics(),
        realApiService.getRecentMessages(),
        realApiService.getInstagramStatus(),
      ]);

      const newData: Partial<DashboardData> = {};
      const newErrors: Record<string, string> = {};

      // Process health check
      if (healthRes.status === 'fulfilled' && healthRes.value.success) {
        newData.health = healthRes.value.data;
      } else {
        newErrors.health = 'Backend health check failed';
      }

      // Process products
      if (productsRes.status === 'fulfilled' && productsRes.value.success) {
        newData.products = productsRes.value.data?.products || [];
      } else {
        newErrors.products = 'Failed to load products';
      }

      // Process analytics
      if (analyticsRes.status === 'fulfilled' && analyticsRes.value.success) {
        newData.analytics = analyticsRes.value.data;
      } else {
        newErrors.analytics = 'Failed to load analytics';
      }

      // Process messages
      if (messagesRes.status === 'fulfilled' && messagesRes.value.success) {
        newData.recentMessages = messagesRes.value.data?.messages || [];
      } else {
        newErrors.messages = 'Failed to load messages';
      }

      // Process Instagram status
      if (instagramRes.status === 'fulfilled' && instagramRes.value.success) {
        newData.instagramStatus = instagramRes.value.data;
      } else {
        newErrors.instagram = 'Failed to load Instagram status';
      }

      setData(newData);
      setErrors(newErrors);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Dashboard load error:', error);
      setErrors({ general: 'Failed to load dashboard data' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isConnected) {
      loadDashboardData();
    }
  }, [isConnected]);

  const handleRefresh = () => {
    loadDashboardData();
  };

  const stats = [
    {
      title: 'Total Messages',
      value: data.analytics?.total_messages?.toLocaleString() || '0',
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: MessageCircle,
      color: 'bg-blue-500',
      error: errors.analytics
    },
    {
      title: 'Total Orders',
      value: data.analytics?.total_orders?.toString() || '0',
      change: '+8.2%',
      changeType: 'positive' as const,
      icon: ShoppingCart,
      color: 'bg-green-500',
      error: errors.analytics
    },
    {
      title: 'Revenue Today',
      value: `${data.analytics?.revenue_today?.toFixed(2) || '0.00'} JOD`,
      change: '+23.1%',
      changeType: 'positive' as const,
      icon: DollarSign,
      color: 'bg-emerald-500',
      error: errors.analytics
    },
    {
      title: 'AI Cost Today',
      value: `$${data.analytics?.ai_cost_today?.toFixed(2) || '0.00'}`,
      change: '-5.3%',
      changeType: 'negative' as const,
      icon: TrendingUp,
      color: 'bg-orange-500',
      error: errors.analytics
    }
  ];

  const performanceMetrics = [
    {
      label: 'Response Rate',
      value: data.analytics?.response_rate || 0,
      max: 100,
      unit: '%',
      color: 'bg-blue-500'
    },
    {
      label: 'Conversion Rate',
      value: data.analytics?.conversion_rate || 0,
      max: 100,
      unit: '%',
      color: 'bg-green-500'
    }
  ];

  if (connectionLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Connecting to backend...</p>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Cannot connect to backend API at {realApiService['baseUrl']}. 
            Please check if the backend is running.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Functional Dashboard</h1>
          <p className="text-slate-500 mt-1">
            Connected to real backend - Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle className="w-4 h-4 mr-2" />
            Backend Connected
          </Badge>
          {data.health && (
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              API v{data.health.version}
            </Badge>
          )}
          <Button onClick={handleRefresh} disabled={loading} size="sm">
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Connection Status */}
      {data.health && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            Backend Status: {data.health.status} - {data.health.message}
          </AlertDescription>
        </Alert>
      )}

      {/* Error Messages */}
      {Object.keys(errors).length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Some data failed to load: {Object.values(errors).join(', ')}
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                  {stat.error ? (
                    <p className="text-lg text-red-500">Error</p>
                  ) : (
                    <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
                  )}
                  {!stat.error && (
                    <div className="flex items-center mt-2">
                      {stat.changeType === 'positive' ? (
                        <ArrowUpRight className="w-4 h-4 text-green-600" />
                      ) : (
                        <ArrowDownRight className="w-4 h-4 text-red-600" />
                      )}
                      <span className={`text-sm font-medium ml-1 ${
                        stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {stat.change}
                      </span>
                      <span className="text-sm text-slate-500 ml-1">vs last period</span>
                    </div>
                  )}
                </div>
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {performanceMetrics.map((metric) => (
              <div key={metric.label}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">{metric.label}</span>
                  <span className="text-sm font-bold text-slate-900">
                    {metric.value}{metric.unit}
                  </span>
                </div>
                <Progress 
                  value={(metric.value / metric.max) * 100} 
                  className="h-2"
                />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Product Catalog */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-green-500" />
              Product Catalog
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            ) : errors.products ? (
              <div className="text-red-500 text-center py-8">
                Failed to load products
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-lg font-semibold text-slate-900">
                  {data.products?.length || 0} Products Available
                </div>
                {data.products?.slice(0, 3).map((product) => (
                  <div key={product.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{product.name}</p>
                      <p className="text-xs text-slate-500">{product.name_en}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-slate-900">
                        {product.price} {product.currency}
                      </p>
                      <Badge 
                        variant={product.in_stock ? "default" : "destructive"}
                        className="text-xs"
                      >
                        {product.in_stock ? 'In Stock' : 'Out of Stock'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Messages */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-blue-500" />
              Recent Messages
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            ) : errors.messages ? (
              <div className="text-orange-500 text-center py-8">
                <MessageCircle className="w-8 h-8 mx-auto mb-2" />
                No recent messages
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-lg font-semibold text-slate-900">
                  {data.recentMessages?.length || 0} Recent Messages
                </div>
                {data.recentMessages?.length > 0 ? (
                  data.recentMessages.slice(0, 3).map((message, index) => (
                    <div key={index} className="border-b pb-2">
                      <p className="text-sm font-medium text-slate-900">{message.customer}</p>
                      <p className="text-xs text-slate-500">{message.message}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 text-center py-4">
                    No messages yet. Start conversations with customers!
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Instagram Status */}
      {data.instagramStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-pink-500" />
              Instagram Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge 
                variant={data.instagramStatus.connected ? "default" : "destructive"}
              >
                {data.instagramStatus.connected ? 'Connected' : 'Not Connected'}
              </Badge>
              {data.instagramStatus.page_info && (
                <span className="text-sm text-slate-600">
                  {data.instagramStatus.page_info.name}
                </span>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 