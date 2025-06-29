import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { apiService, type DashboardAnalytics, type Order } from '../services/api';
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
  Loader2
} from 'lucide-react';

export function Dashboard() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard data
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await apiService.getDashboardAnalytics();
        
        if (response.data) {
          setAnalytics(response.data);
        } else {
          setError(response.error || 'Failed to load dashboard data');
        }
      } catch (err) {
        setError('Network error loading dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  // Create stats array from real data
  const stats = analytics ? [
    {
      title: 'Total Orders',
      value: analytics.total_orders.toLocaleString(),
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: ShoppingCart,
      color: 'bg-green-500'
    },
    {
      title: 'Total Revenue',
      value: `${analytics.total_revenue.toLocaleString()} JOD`,
      change: '+23.1%',
      changeType: 'positive' as const,
      icon: DollarSign,
      color: 'bg-emerald-500'
    },
    {
      title: 'Total Products',
      value: analytics.total_products.toString(),
      change: '+8.2%',
      changeType: 'positive' as const,
      icon: MessageCircle,
      color: 'bg-blue-500'
    },
    {
      title: 'Pending Orders',
      value: analytics.pending_orders.toString(),
      change: '-5.3%',
      changeType: 'negative' as const,
      icon: Clock,
      color: 'bg-orange-500'
    }
  ] : [];

  const performanceMetrics = [
    {
      label: 'Order Conversion',
      value: analytics ? Math.round((analytics.confirmed_orders / analytics.total_orders) * 100) : 0,
      max: 100,
      unit: '%',
      color: 'bg-green-500'
    },
    {
      label: 'Pending Rate', 
      value: analytics ? Math.round((analytics.pending_orders / analytics.total_orders) * 100) : 0,
      max: 100,
      unit: '%',
      color: 'bg-orange-500'
    },
    {
      label: 'Avg Order Value',
      value: analytics ? Math.round(analytics.total_revenue / analytics.total_orders) : 0,
      max: 200,
      unit: ' JOD',
      color: 'bg-blue-500'
    }
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-slate-500 mt-1">Loading your Instagram store data...</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
            <span className="text-slate-600">Loading dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-slate-500 mt-1">Welcome back to your Instagram store.</p>
          </div>
        </div>
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {error}
          </AlertDescription>
        </Alert>
        <div className="text-center">
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">
            Welcome back! Here's what's happening with your Instagram store.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            AI Agent Online
          </Badge>
          <Button>
            <Eye className="w-4 h-4 mr-2" />
            View Live Chat
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
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
                    <span className="text-sm text-slate-500 ml-1">vs last month</span>
                  </div>
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

        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-green-500" />
              Recent Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics?.recent_orders && analytics.recent_orders.length > 0 ? (
                analytics.recent_orders.slice(0, 4).map((order) => (
                  <div key={order.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{order.customer}</p>
                      <p className="text-xs text-slate-500">{order.sku}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-slate-900">{order.total_amount} JOD</p>
                      <Badge 
                        variant={
                          order.status === 'delivered' ? 'default' :
                          order.status === 'shipped' ? 'secondary' :
                          order.status === 'confirmed' ? 'outline' : 'destructive'
                        }
                        className="text-xs"
                      >
                        {order.status}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-slate-500">No recent orders</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Top Products */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Top Products
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics?.top_products && analytics.top_products.length > 0 ? (
                analytics.top_products.slice(0, 3).map((product) => (
                  <div key={product.id} className="border-l-4 border-yellow-200 pl-3">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-slate-900">{product.name}</p>
                      <Badge variant="outline" className="text-xs">
                        Stock: {product.stock_quantity || 0}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-600">{product.sku}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <p className="text-sm font-bold text-slate-900">{product.price_jod} JOD</p>
                      {product.category && (
                        <Badge variant="secondary" className="text-xs">
                          {product.category}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-slate-500">No products available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
