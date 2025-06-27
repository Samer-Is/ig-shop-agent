import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
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
  Eye
} from 'lucide-react';
import { dashboardStats, orders, conversations } from '../data/mockData';

export function Dashboard() {
  const stats = [
    {
      title: 'Total Conversations',
      value: dashboardStats.total_conversations.toLocaleString(),
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: MessageCircle,
      color: 'bg-blue-500'
    },
    {
      title: 'Active Orders',
      value: dashboardStats.active_orders.toString(),
      change: '+8.2%',
      changeType: 'positive' as const,
      icon: ShoppingCart,
      color: 'bg-green-500'
    },
    {
      title: 'Monthly Revenue',
      value: `${dashboardStats.revenue_this_month.toLocaleString()} JOD`,
      change: '+23.1%',
      changeType: 'positive' as const,
      icon: DollarSign,
      color: 'bg-emerald-500'
    },
    {
      title: 'AI Cost This Month',
      value: `$${dashboardStats.ai_cost_this_month.toFixed(2)}`,
      change: '-5.3%',
      changeType: 'negative' as const,
      icon: TrendingUp,
      color: 'bg-orange-500'
    }
  ];

  const performanceMetrics = [
    {
      label: 'Customer Satisfaction',
      value: dashboardStats.customer_satisfaction,
      max: 5,
      unit: '★',
      color: 'bg-yellow-500'
    },
    {
      label: 'Avg Response Time',
      value: dashboardStats.response_time_avg,
      max: 5,
      unit: 'min',
      color: 'bg-blue-500'
    },
    {
      label: 'Conversion Rate',
      value: dashboardStats.conversion_rate,
      max: 100,
      unit: '%',
      color: 'bg-green-500'
    }
  ];

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
              {orders.slice(0, 4).map((order) => (
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
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Conversations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-blue-500" />
              Recent Conversations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {conversations.slice(0, 3).map((conv) => (
                <div key={conv.id} className="border-l-4 border-blue-200 pl-3">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-slate-900">{conv.sender}</p>
                    <Badge variant={conv.ai_generated ? 'secondary' : 'outline'} className="text-xs">
                      {conv.ai_generated ? 'AI' : 'Customer'}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-2">{conv.text}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span className="text-xs text-slate-400">
                      {new Date(conv.ts).toLocaleTimeString('en-US', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Products */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-500" />
            Top Performing Products
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dashboardStats.top_products.map((product) => (
              <div key={product.id} className="flex items-center gap-4 p-4 border border-slate-200 rounded-lg">
                <div className="w-16 h-16 bg-slate-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">👗</span>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-slate-900">{product.name}</h4>
                  <p className="text-sm text-slate-500">{product.sku}</p>
                  <p className="text-sm font-bold text-green-600 mt-1">{product.price_jod} JOD</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
