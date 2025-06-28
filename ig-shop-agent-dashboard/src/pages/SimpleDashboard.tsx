import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { AlertCircle, CheckCircle, RefreshCw, TrendingUp, Users, MessageSquare, ShoppingBag } from 'lucide-react';

// Simple direct API connection
const API_URL = 'https://igshop-dev-functions-v2.azurewebsites.net/api';

interface Product {
  id: string;
  name: string;
  name_ar: string;
  price: number;
  currency: string;
  stock: number;
}

interface Health {
  status: string;
  message: string;
  version: string;
  timestamp: string;
}

interface Analytics {
  total_messages: number;
  total_orders: number;
  response_rate: number;
  conversion_rate: number;
}

export function SimpleDashboard() {
  const [health, setHealth] = useState<Health | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Direct API calls
  const fetchHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setHealth(data);
      setConnected(response.ok);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      setConnected(false);
      return false;
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/catalog`);
      const data = await response.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Products fetch failed:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_URL}/analytics`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Analytics fetch failed:', error);
    }
  };

  const refreshData = async () => {
    setLoading(true);
    const isHealthy = await fetchHealth();
    if (isHealthy) {
      await Promise.all([
        fetchProducts(),
        fetchAnalytics()
      ]);
    }
    setLastUpdate(new Date());
    setLoading(false);
  };

  useEffect(() => {
    refreshData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">IG Shop Dashboard</h1>
          <p className="text-gray-600">Instagram DM Automation & Business Management</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
          <Button onClick={refreshData} disabled={loading} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {connected ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            Backend Connection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Badge variant={connected ? "default" : "destructive"} className="mb-2">
                {connected ? "Connected" : "Disconnected"}
              </Badge>
              {health && (
                <div className="space-y-1 text-sm">
                  <p><strong>Status:</strong> {health.status}</p>
                  <p><strong>Version:</strong> {health.version}</p>
                  <p><strong>Message:</strong> {health.message}</p>
                </div>
              )}
            </div>
            <div className="text-right text-sm text-gray-500">
              <p>Backend API</p>
              <p className="font-mono text-xs">...functions-v2.azurewebsites.net</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <ShoppingBag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.length}</div>
            <p className="text-xs text-muted-foreground">
              Active in catalog
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_messages || 0}</div>
            <p className="text-xs text-muted-foreground">
              Total processed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Orders</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_orders || 0}</div>
            <p className="text-xs text-muted-foreground">
              Completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.conversion_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">
              Message to order
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Products Section */}
      <Card>
        <CardHeader>
          <CardTitle>Product Catalog</CardTitle>
          <CardDescription>
            Current products in your store
          </CardDescription>
        </CardHeader>
        <CardContent>
          {products.length > 0 ? (
            <div className="space-y-4">
              {products.map((product) => (
                <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">{product.name}</h3>
                    <p className="text-sm text-gray-600">{product.name_ar}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{product.price} {product.currency}</p>
                    <p className="text-sm text-gray-600">{product.stock} in stock</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              {connected ? "No products found" : "Connect to backend to load products"}
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span>Backend API</span>
              <Badge variant={connected ? "default" : "destructive"}>
                {connected ? "Online" : "Offline"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>AI Agent</span>
              <Badge variant={connected ? "default" : "secondary"}>
                {connected ? "Active" : "Standby"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Instagram Integration</span>
              <Badge variant="secondary">
                Ready
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Auto-refresh</span>
              <Badge variant="default">
                30s interval
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 