import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  Instagram, 
  MessageCircle, 
  Send, 
  User, 
  Bot,
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  ShoppingBag,
  TrendingUp
} from 'lucide-react';

const API_URL = 'https://igshop-dev-functions-v2.azurewebsites.net/api';

interface Product {
  id: string;
  name: string;
  name_en?: string;
  price: number;
  currency: string;
  stock: number;
}

interface Message {
  id: number;
  customer_id: string;
  customer_name: string;
  message: string;
  ai_response: string;
  intent: string;
  language: string;
  timestamp: string;
}

interface Analytics {
  total_messages: number;
  total_orders: number;
  total_customers: number;
  response_rate: number;
  conversion_rate: number;
}

export function WorkingDashboard() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState<Product[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testResponse, setTestResponse] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Load all data
  const loadData = async () => {
    setLoading(true);
    try {
      // Test backend connection
      const healthResponse = await fetch(`${API_URL}/health`);
      if (healthResponse.ok) {
        setBackendConnected(true);
        
        // Load products
        try {
          const productsResponse = await fetch(`${API_URL}/catalog`);
          if (productsResponse.ok) {
            const productsData = await productsResponse.json();
            setProducts(productsData.products || []);
          }
        } catch (e) {
          console.log('Products not available');
        }
        
        // Load messages
        try {
          const messagesResponse = await fetch(`${API_URL}/messages/recent`);
          if (messagesResponse.ok) {
            const messagesData = await messagesResponse.json();
            setMessages(messagesData.messages || []);
          }
        } catch (e) {
          console.log('Messages not available');
        }
        
        // Load analytics
        try {
          const analyticsResponse = await fetch(`${API_URL}/analytics`);
          if (analyticsResponse.ok) {
            const analyticsData = await analyticsResponse.json();
            setAnalytics(analyticsData);
          }
        } catch (e) {
          console.log('Analytics not available');
        }
        
      } else {
        setBackendConnected(false);
      }
    } catch (error) {
      console.error('Failed to connect to backend:', error);
      setBackendConnected(false);
    } finally {
      setLoading(false);
      setLastUpdate(new Date());
    }
  };

  // Test AI agent
  const testAI = async () => {
    if (!testMessage.trim()) return;
    
    setTestLoading(true);
    setTestResponse('');
    
    try {
      const response = await fetch(`${API_URL}/ai/test-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: testMessage })
      });
      
      if (response.ok) {
        const result = await response.json();
        setTestResponse(result.response || 'No response generated');
      } else {
        setTestResponse('Error: Failed to get AI response');
      }
    } catch (error) {
      setTestResponse('Error: Could not connect to AI agent');
    } finally {
      setTestLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">IG Shop Agent</h1>
          <p className="text-gray-600">Instagram DM Automation Platform</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            Updated: {lastUpdate.toLocaleTimeString()}
          </span>
          <Button onClick={loadData} disabled={loading} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Backend Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {backendConnected ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            Backend Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Badge variant={backendConnected ? "default" : "destructive"}>
                {backendConnected ? "Connected" : "Disconnected"}
              </Badge>
              <p className="text-sm text-gray-600 mt-2">
                {backendConnected 
                  ? "Instagram DM automation backend is running" 
                  : "Cannot connect to backend API"
                }
              </p>
            </div>
            <div className="text-right text-sm text-gray-500">
              <p>Azure Functions</p>
              <p className="font-mono text-xs">...functions-v2.azurewebsites.net</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Products</CardTitle>
            <ShoppingBag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.length}</div>
            <p className="text-xs text-muted-foreground">In catalog</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages</CardTitle>
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_messages || 0}</div>
            <p className="text-xs text-muted-foreground">Processed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Customers</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.total_customers || 0}</div>
            <p className="text-xs text-muted-foreground">Active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.response_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">AI accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Test AI Agent */}
      <Card>
        <CardHeader>
          <CardTitle>Test AI Agent</CardTitle>
          <CardDescription>
            Test your Instagram DM automation with sample messages
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Textarea
              placeholder="Test message in Arabic or English (e.g., 'أريد شراء قميص' or 'I want to buy a shirt')"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              rows={3}
            />
            <Button 
              onClick={testAI} 
              disabled={testLoading || !testMessage.trim() || !backendConnected}
              className="w-full"
            >
              {testLoading ? 'Processing...' : 'Test AI Response'}
              <Send className="h-4 w-4 ml-2" />
            </Button>
            {testResponse && (
              <Alert>
                <Bot className="h-4 w-4" />
                <AlertDescription>
                  <strong>AI Response:</strong><br />
                  {testResponse}
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Products */}
      <Card>
        <CardHeader>
          <CardTitle>Product Catalog</CardTitle>
          <CardDescription>Products available for Instagram customers</CardDescription>
        </CardHeader>
        <CardContent>
          {products.length > 0 ? (
            <div className="grid gap-4">
              {products.map((product) => (
                <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">{product.name}</h3>
                    {product.name_en && (
                      <p className="text-sm text-gray-600">{product.name_en}</p>
                    )}
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
              {backendConnected ? "No products loaded" : "Connect to backend to see products"}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Messages */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Instagram Messages</CardTitle>
          <CardDescription>Live DM conversations and AI responses</CardDescription>
        </CardHeader>
        <CardContent>
          {messages.length > 0 ? (
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-blue-600" />
                      <span className="font-semibold text-sm">{message.customer_name}</span>
                      <Badge variant="outline" className="text-xs">{message.language}</Badge>
                      <Badge variant="secondary" className="text-xs">{message.intent}</Badge>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-900 mb-3">{message.message}</p>
                  <div className="bg-green-50 p-3 rounded border-l-4 border-green-500">
                    <div className="flex items-center gap-2 mb-1">
                      <Bot className="h-3 w-3 text-green-600" />
                      <span className="text-xs font-semibold text-green-800">AI Response:</span>
                    </div>
                    <p className="text-sm text-green-800">{message.ai_response}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No Instagram messages yet</p>
              <p className="text-xs">Messages will appear here when customers send DMs</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instagram Integration Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Instagram className="h-5 w-5 text-pink-600" />
            Instagram Integration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>Webhook Endpoint</span>
              <Badge variant="default">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>AI Agent</span>
              <Badge variant={backendConnected ? "default" : "secondary"}>
                {backendConnected ? "Ready" : "Offline"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Message Processing</span>
              <Badge variant="default">Enabled</Badge>
            </div>
            <div className="text-sm text-gray-600">
              <p><strong>Webhook URL:</strong> {API_URL}/webhook/instagram</p>
              <p><strong>Verify Token:</strong> igshop_webhook_verify_2024</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 