import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  DollarSign, 
  MessageCircle, 
  Users, 
  Download,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  Zap
} from 'lucide-react';
import { apiService } from '../services/api';

export function Analytics() {
  // Mock data for charts
  const conversationData = [
    { day: 'Mon', conversations: 45, orders: 8 },
    { day: 'Tue', conversations: 52, orders: 12 },
    { day: 'Wed', conversations: 38, orders: 6 },
    { day: 'Thu', conversations: 67, orders: 15 },
    { day: 'Fri', conversations: 89, orders: 22 },
    { day: 'Sat', conversations: 94, orders: 28 },
    { day: 'Sun', conversations: 71, orders: 18 }
  ];

  const revenueData = [
    { month: 'Jan', revenue: 4500, cost: 120 },
    { month: 'Feb', revenue: 5200, cost: 145 },
    { month: 'Mar', revenue: 4800, cost: 132 },
    { month: 'Apr', revenue: 6100, cost: 168 },
    { month: 'May', revenue: 7300, cost: 195 },
    { month: 'Jun', revenue: 8750, cost: 230 }
  ];

  const customerSatisfactionData = [
    { name: 'Excellent', value: 65, color: '#10b981' },
    { name: 'Good', value: 25, color: '#3b82f6' },
    { name: 'Average', value: 8, color: '#f59e0b' },
    { name: 'Poor', value: 2, color: '#ef4444' }
  ];

  const responseTimeData = [
    { hour: '00', time: 0.8 },
    { hour: '06', time: 1.2 },
    { hour: '12', time: 2.1 },
    { hour: '18', time: 1.8 },
    { hour: '24', time: 0.9 }
  ];

  const topProducts = [
    { name: 'فستان صيفي أنيق', sales: 45, revenue: 3825 },
    { name: 'بلوزة كاجوال عصرية', sales: 32, revenue: 1440 },
    { name: 'حقيبة يد أنيقة', sales: 18, revenue: 2160 },
    { name: 'فستان سهرة فاخر', sales: 12, revenue: 3000 },
    { name: 'حذاء كعب عالي', sales: 28, revenue: 2660 }
  ];

  const keyMetrics = [
    {
      title: 'Total Revenue',
      value: '8,750 JOD',
      change: '+23.1%',
      changeType: 'positive' as const,
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      title: 'Conversations',
      value: '1,523',
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: MessageCircle,
      color: 'text-blue-600'
    },
    {
      title: 'Conversion Rate',
      value: '18.5%',
      change: '+3.2%',
      changeType: 'positive' as const,
      icon: Target,
      color: 'text-purple-600'
    },
    {
      title: 'AI Cost',
      value: '$342.50',
      change: '-5.3%',
      changeType: 'negative' as const,
      icon: Zap,
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics</h1>
          <p className="text-slate-500 mt-1">
            Track your business performance and AI agent effectiveness
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select defaultValue="30d">
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {keyMetrics.map((metric) => (
          <Card key={metric.title}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500">{metric.title}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{metric.value}</p>
                  <div className="flex items-center mt-2">
                    {metric.changeType === 'positive' ? (
                      <ArrowUpRight className="w-4 h-4 text-green-600" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 text-red-600" />
                    )}
                    <span className={`text-sm font-medium ml-1 ${
                      metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metric.change}
                    </span>
                    <span className="text-sm text-slate-500 ml-1">vs last period</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg bg-slate-50`}>
                  <metric.icon className={`w-6 h-6 ${metric.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversations & Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Conversations & Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={conversationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="conversations" fill="#3b82f6" name="Conversations" />
                <Bar dataKey="orders" fill="#10b981" name="Orders" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Customer Satisfaction */}
        <Card>
          <CardHeader>
            <CardTitle>Customer Satisfaction</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={customerSatisfactionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {customerSatisfactionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue vs AI Cost */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue vs AI Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  name="Revenue (JOD)"
                />
                <Line 
                  type="monotone" 
                  dataKey="cost" 
                  stroke="#ef4444" 
                  strokeWidth={3}
                  name="AI Cost (USD)"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Response Time */}
        <Card>
          <CardHeader>
            <CardTitle>Average Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="time" 
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  fillOpacity={0.3}
                  name="Response Time (min)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top Products */}
      <Card>
        <CardHeader>
          <CardTitle>Top Performing Products</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topProducts.map((product, index) => (
              <div key={product.name} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-slate-600">#{index + 1}</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-slate-900">{product.name}</h4>
                    <p className="text-sm text-slate-500">{product.sales} sales this month</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">{product.revenue.toLocaleString()} JOD</p>
                  <p className="text-sm text-slate-500">Total revenue</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
