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
  Clock, 
  CheckCircle, 
  AlertCircle,
  Bot,
  Settings,
  RefreshCw,
  Heart,
  ShoppingBag
} from 'lucide-react';

interface InstagramMessage {
  id: string;
  sender: string;
  text: string;
  timestamp: string;
  is_from_user: boolean;
  response_generated?: boolean;
  ai_response?: string;
  intent?: string;
  language?: string;
}

interface InstagramConnection {
  connected: boolean;
  page_name?: string;
  page_id?: string;
  instagram_handle?: string;
  last_sync?: string;
}

interface AIStats {
  messages_processed: number;
  responses_generated: number;
  accuracy_rate: number;
  avg_response_time: number;
  languages_detected: string[];
}

export function InstagramAgent() {
  const [connection, setConnection] = useState<InstagramConnection>({ connected: false });
  const [messages, setMessages] = useState<InstagramMessage[]>([]);
  const [aiStats, setAiStats] = useState<AIStats>({
    messages_processed: 0,
    responses_generated: 0,
    accuracy_rate: 0,
    avg_response_time: 0,
    languages_detected: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testResponse, setTestResponse] = useState('');
  const [testLoading, setTestLoading] = useState(false);

  // Load Instagram connection status and messages
  useEffect(() => {
    loadInstagramData();
    
    // Auto-refresh every 10 seconds for real-time updates
    const interval = setInterval(loadInstagramData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadInstagramData = async () => {
    try {
      // Load Instagram connection status
      const statusResponse = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/instagram/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setConnection(statusData);
      }

      // Load recent messages
      const messagesResponse = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/messages/recent');
      if (messagesResponse.ok) {
        const messagesData = await messagesResponse.json();
        setMessages(messagesData.messages || []);
      }

      // Load AI stats
      const statsResponse = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/ai/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setAiStats(statsData);
      }

      setError(null);
    } catch (error) {
      console.error('Failed to load Instagram data:', error);
      setError('Failed to load Instagram data');
    } finally {
      setLoading(false);
    }
  };

  // Connect Instagram account
  const handleInstagramConnect = async () => {
    setLoading(true);
    try {
      // Get Instagram OAuth URL
      const configResponse = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/instagram/config');
      const config = await configResponse.json();

      const oauthUrl = `https://www.facebook.com/v18.0/dialog/oauth?` + 
        new URLSearchParams({
          client_id: config.app_id,
          redirect_uri: config.redirect_uri,
          scope: 'instagram_basic,instagram_manage_messages,pages_manage_metadata,pages_read_engagement',
          response_type: 'code',
          state: Math.random().toString(36).substring(2, 15)
        });

      // Open OAuth popup
      const popup = window.open(oauthUrl, 'instagram-oauth', 'width=600,height=600');
      
      // Listen for OAuth completion
      const handleMessage = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === 'INSTAGRAM_OAUTH_SUCCESS') {
          popup?.close();
          handleOAuthSuccess(event.data.code);
          window.removeEventListener('message', handleMessage);
        }
      };

      window.addEventListener('message', handleMessage);

    } catch (error) {
      setError('Failed to initiate Instagram connection');
      setLoading(false);
    }
  };

  const handleOAuthSuccess = async (code: string) => {
    try {
      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/instagram/oauth/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      const result = await response.json();
      if (response.ok) {
        await loadInstagramData(); // Refresh data
      } else {
        setError(result.error || 'Failed to complete Instagram connection');
      }
    } catch (error) {
      setError('Failed to complete Instagram connection');
    } finally {
      setLoading(false);
    }
  };

  // Test AI agent
  const handleTestMessage = async () => {
    if (!testMessage.trim()) return;

    setTestLoading(true);
    setTestResponse('');

    try {
      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/ai/test-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: testMessage })
      });

      const result = await response.json();
      if (response.ok) {
        setTestResponse(result.response);
      } else {
        setTestResponse('Error: ' + (result.error || 'Failed to process message'));
      }
    } catch (error) {
      setTestResponse('Error: Failed to connect to AI agent');
    } finally {
      setTestLoading(false);
    }
  };

  // Disconnect Instagram
  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect Instagram? This will stop DM automation.')) return;

    setLoading(true);
    try {
      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/instagram/disconnect', {
        method: 'POST'
      });

      if (response.ok) {
        setConnection({ connected: false });
        setMessages([]);
      } else {
        setError('Failed to disconnect Instagram');
      }
    } catch (error) {
      setError('Failed to disconnect Instagram');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Instagram DM Agent</h1>
          <p className="text-gray-600">AI-powered Instagram message automation</p>
        </div>
        <Button onClick={loadInstagramData} disabled={loading} variant="outline" size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Instagram Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Instagram className="h-5 w-5 text-pink-600" />
            Instagram Connection
          </CardTitle>
        </CardHeader>
        <CardContent>
          {connection.connected ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant="default" className="bg-green-500">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Connected
                  </Badge>
                  <div>
                    <p className="font-semibold">@{connection.instagram_handle}</p>
                    <p className="text-sm text-gray-600">{connection.page_name}</p>
                  </div>
                </div>
                <Button variant="outline" onClick={handleDisconnect} size="sm">
                  Disconnect
                </Button>
              </div>
              <div className="text-sm text-gray-500">
                Last synced: {connection.last_sync ? new Date(connection.last_sync).toLocaleString() : 'Never'}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Instagram className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-semibold mb-2">Connect Your Instagram Business Account</h3>
              <p className="text-gray-600 mb-6">
                Enable AI-powered DM automation by connecting your Instagram Business page
              </p>
              <Button onClick={handleInstagramConnect} disabled={loading} className="bg-pink-600 hover:bg-pink-700">
                {loading ? 'Connecting...' : 'Connect Instagram'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages Processed</CardTitle>
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{aiStats.messages_processed}</div>
            <p className="text-xs text-muted-foreground">Total Instagram DMs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Responses</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{aiStats.responses_generated}</div>
            <p className="text-xs text-muted-foreground">Automated replies</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{aiStats.avg_response_time}s</div>
            <p className="text-xs text-muted-foreground">Average response</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Accuracy Rate</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{aiStats.accuracy_rate}%</div>
            <p className="text-xs text-muted-foreground">Customer satisfaction</p>
          </CardContent>
        </Card>
      </div>

      {/* Test AI Agent */}
      <Card>
        <CardHeader>
          <CardTitle>Test AI Agent</CardTitle>
          <CardDescription>
            Test your AI assistant with sample messages in Arabic or English
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Textarea
                placeholder="Type a test message in Arabic or English... (e.g., 'أريد شراء قميص أبيض' or 'I want to buy a white shirt')"
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                rows={3}
              />
            </div>
            <Button 
              onClick={handleTestMessage} 
              disabled={testLoading || !testMessage.trim()}
              className="w-full"
            >
              {testLoading ? 'Processing...' : 'Test AI Response'}
              <Send className="h-4 w-4 ml-2" />
            </Button>
            {testResponse && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">AI Response:</p>
                <p className="text-gray-900">{testResponse}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Messages */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Instagram Messages</CardTitle>
          <CardDescription>
            Live feed of Instagram DMs and AI responses
          </CardDescription>
        </CardHeader>
        <CardContent>
          {messages.length > 0 ? (
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {message.is_from_user ? (
                        <User className="h-4 w-4 text-blue-600" />
                      ) : (
                        <Bot className="h-4 w-4 text-green-600" />
                      )}
                      <span className="font-semibold text-sm">
                        {message.is_from_user ? message.sender : 'IG Shop Agent'}
                      </span>
                      {message.language && (
                        <Badge variant="outline" className="text-xs">
                          {message.language}
                        </Badge>
                      )}
                      {message.intent && (
                        <Badge variant="secondary" className="text-xs">
                          {message.intent}
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(message.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-900 mb-2">{message.text}</p>
                  {message.ai_response && (
                    <div className="mt-3 p-3 bg-green-50 rounded border-l-4 border-green-500">
                      <p className="text-sm text-green-800">{message.ai_response}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              {connection.connected ? (
                <>
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No messages yet. Start a conversation on Instagram!</p>
                </>
              ) : (
                <>
                  <Instagram className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Connect Instagram to see messages here</p>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Language Support */}
      <Card>
        <CardHeader>
          <CardTitle>AI Capabilities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Languages Supported</h4>
              <div className="flex flex-wrap gap-2">
                <Badge>Arabic (Jordanian)</Badge>
                <Badge>English</Badge>
                <Badge>Mixed Language</Badge>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Features</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <p>✅ Product recommendations</p>
                <p>✅ Order creation</p>
                <p>✅ Customer support</p>
                <p>✅ Conversation memory</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 