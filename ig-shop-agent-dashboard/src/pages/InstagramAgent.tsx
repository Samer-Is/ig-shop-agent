import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';
import { apiService } from '../services/api';
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
  ShoppingBag,
  Link
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
    messages_processed: 147,
    responses_generated: 142,
    accuracy_rate: 96.6,
    avg_response_time: 1.2,
    languages_detected: ['Arabic', 'English']
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testResponse, setTestResponse] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [connectingInstagram, setConnectingInstagram] = useState(false);

  // Load Instagram connection status and messages
  useEffect(() => {
    loadInstagramData();
    
    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(loadInstagramData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadInstagramData = async () => {
    try {
      // Check health and connection status
      const healthResponse = await apiService.healthCheck();
      if (healthResponse.data) {
        // For now, we'll simulate connection status based on user data
        // In production, this would come from the backend
        setConnection({
          connected: false, // Will be updated when Instagram is actually connected
          instagram_handle: '',
          last_sync: new Date().toISOString()
        });
      }

      // Load conversations (placeholder for now)
      const conversations = await apiService.getConversations();
      setMessages(conversations.map(conv => ({
        id: conv.id.toString(),
        sender: 'Customer',
        text: conv.text,
        timestamp: conv.created_at,
        is_from_user: !conv.ai_generated,
        response_generated: conv.ai_generated
      })));

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
    setConnectingInstagram(true);
    setError(null);
    
    try {
      // Get Instagram OAuth URL from backend
      const response = await apiService.getInstagramAuthUrl();
      
      if (response.data?.auth_url) {
        // Redirect to Instagram OAuth
        window.location.href = response.data.auth_url;
      } else {
        setError(response.error || 'Failed to get Instagram authorization URL');
      }
    } catch (error) {
      console.error('Instagram connection error:', error);
      setError('Failed to initiate Instagram connection');
    } finally {
      setConnectingInstagram(false);
    }
  };

  // Test AI agent
  const handleTestMessage = async () => {
    if (!testMessage.trim()) return;

    setTestLoading(true);
    setTestResponse('');

    try {
      const response = await apiService.testAIResponse(testMessage);
      
      if (response.data) {
        setTestResponse(response.data.response);
      } else {
        setTestResponse('Error: ' + (response.error || 'Failed to process message'));
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
      // For now, just update the UI
      setConnection({ connected: false });
      setError(null);
    } catch (error) {
      setError('Failed to disconnect Instagram');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Instagram AI Agent</h1>
          <p className="text-slate-500 mt-1">
            Manage your Instagram DM automation and AI responses
          </p>
        </div>
        <Button onClick={loadInstagramData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Instagram Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Instagram className="h-5 w-5" />
            Instagram Connection
          </CardTitle>
          <CardDescription>
            Connect your Instagram Business account to enable DM automation
          </CardDescription>
        </CardHeader>
        <CardContent>
          {connection.connected ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="font-medium text-green-900">
                      Connected to @{connection.instagram_handle}
                    </p>
                    <p className="text-sm text-green-700">
                      Last sync: {connection.last_sync ? new Date(connection.last_sync).toLocaleString() : 'Never'}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={handleDisconnect}>
                  Disconnect
                </Button>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <p className="text-2xl font-bold text-slate-900">{aiStats.messages_processed}</p>
                  <p className="text-sm text-slate-600">Messages Processed</p>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <p className="text-2xl font-bold text-slate-900">{aiStats.responses_generated}</p>
                  <p className="text-sm text-slate-600">AI Responses</p>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <p className="text-2xl font-bold text-slate-900">{aiStats.accuracy_rate}%</p>
                  <p className="text-sm text-slate-600">Accuracy Rate</p>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <p className="text-2xl font-bold text-slate-900">{aiStats.avg_response_time}s</p>
                  <p className="text-sm text-slate-600">Avg Response Time</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Instagram className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 mb-2">
                Connect Your Instagram Account
              </h3>
              <p className="text-slate-600 mb-6 max-w-md mx-auto">
                Connect your Instagram Business account to start receiving and responding to DMs automatically with AI.
              </p>
              <Button 
                onClick={handleInstagramConnect} 
                className="bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700"
                disabled={connectingInstagram}
              >
                {connectingInstagram ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Link className="h-4 w-4 mr-2" />
                    Connect Instagram
                  </>
                )}
              </Button>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-900 mb-2">Requirements:</h4>
                <ul className="text-sm text-blue-800 space-y-1 text-left max-w-sm mx-auto">
                  <li>• Instagram Business or Creator account</li>
                  <li>• Account must be linked to a Facebook Page</li>
                  <li>• Page must have Instagram messaging enabled</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Agent Testing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Test AI Agent
          </CardTitle>
          <CardDescription>
            Test how the AI agent responds to customer messages
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Test Message</label>
            <Input
              placeholder="Type a customer message in Arabic or English..."
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleTestMessage()}
            />
          </div>
          
          <Button 
            onClick={handleTestMessage} 
            disabled={testLoading || !testMessage.trim()}
            className="w-full"
          >
            {testLoading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Test AI Response
              </>
            )}
          </Button>
          
          {testResponse && (
            <div className="p-4 bg-slate-50 rounded-lg border">
              <div className="flex items-start gap-3">
                <Bot className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-slate-900 mb-1">AI Response:</p>
                  <p className="text-slate-700">{testResponse}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Messages */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Recent Messages
          </CardTitle>
          <CardDescription>
            Latest Instagram DM conversations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-600">No messages yet</p>
              <p className="text-sm text-slate-500">
                {connection.connected 
                  ? "Messages will appear here when customers start DMing your Instagram account"
                  : "Connect your Instagram account to see messages here"
                }
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div 
                  key={message.id}
                  className={`p-4 rounded-lg border ${
                    message.is_from_user 
                      ? 'bg-white border-slate-200' 
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      {message.is_from_user ? (
                        <User className="h-5 w-5 text-slate-600 mt-0.5" />
                      ) : (
                        <Bot className="h-5 w-5 text-blue-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-slate-900">
                            {message.is_from_user ? message.sender : 'AI Agent'}
                          </span>
                          {message.response_generated && (
                            <Badge variant="secondary" className="text-xs">
                              AI Generated
                            </Badge>
                          )}
                        </div>
                        <p className="text-slate-700">{message.text}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <Clock className="h-3 w-3" />
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 