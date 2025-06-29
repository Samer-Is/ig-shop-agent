import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Search,
  Filter,
  Settings,
  Zap,
  Clock,
  DollarSign,
  Activity
} from 'lucide-react';
import { apiService } from '../services/api';
import { Conversation, ChatMessage } from '../types';

export function Conversations() {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Group conversations by sender (simulate chat threads)
  const chatThreads = conversations.reduce((acc, conv) => {
    if (!acc[conv.sender]) {
      acc[conv.sender] = [];
    }
    acc[conv.sender].push(conv);
    return acc;
  }, {} as Record<string, Conversation[]>);

  const threadList = Object.entries(chatThreads).map(([sender, messages]) => ({
    sender,
    messages: messages.sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()),
    lastMessage: messages[messages.length - 1],
    unreadCount: Math.floor(Math.random() * 3) // Mock unread count
  }));

  const filteredThreads = threadList.filter(thread =>
    thread.sender.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedThread = selectedConversation 
    ? threadList.find(t => t.sender === selectedConversation)
    : null;

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    // Mock sending message
    console.log('Sending message:', newMessage);
    setNewMessage('');
  };

  const conversationStats = {
    total: Object.keys(chatThreads).length,
    active: Object.keys(chatThreads).filter(sender => {
      const lastMessage = chatThreads[sender][chatThreads[sender].length - 1];
      const dayAgo = new Date();
      dayAgo.setDate(dayAgo.getDate() - 1);
      return new Date(lastMessage.ts) > dayAgo;
    }).length,
    avgResponseTime: 1.2,
    totalTokensToday: conversations.reduce((sum, conv) => sum + conv.tokens_in + conv.tokens_out, 0)
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Conversations</h1>
          <p className="text-slate-500 mt-1">
            Monitor and manage AI conversations with customers
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <Activity className="w-3 h-3 mr-1" />
            AI Agent Active
          </Badge>
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            AI Settings
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Total Conversations</p>
                <p className="text-2xl font-bold text-slate-900">{conversationStats.total}</p>
              </div>
              <MessageCircle className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Active Today</p>
                <p className="text-2xl font-bold text-slate-900">{conversationStats.active}</p>
              </div>
              <Zap className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Avg Response Time</p>
                <p className="text-2xl font-bold text-slate-900">{conversationStats.avgResponseTime}min</p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Tokens Today</p>
                <p className="text-2xl font-bold text-slate-900">{conversationStats.totalTokensToday.toLocaleString()}</p>
              </div>
              <DollarSign className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
        {/* Conversation List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Recent Conversations</span>
              <Badge variant="secondary">{filteredThreads.length}</Badge>
            </CardTitle>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[400px]">
              <div className="space-y-1 p-4">
                {filteredThreads.map((thread) => (
                  <div
                    key={thread.sender}
                    onClick={() => setSelectedConversation(thread.sender)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedConversation === thread.sender
                        ? 'bg-blue-50 border border-blue-200'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="bg-blue-100 text-blue-700 text-xs">
                            {thread.sender.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <h4 className="font-medium text-slate-900 text-sm">{thread.sender}</h4>
                      </div>
                      {thread.unreadCount > 0 && (
                        <Badge variant="destructive" className="text-xs w-5 h-5 flex items-center justify-center p-0">
                          {thread.unreadCount}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 mb-1">
                      {thread.lastMessage.text}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400">
                        {new Date(thread.lastMessage.ts).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                      <Badge variant={thread.lastMessage.ai_generated ? 'secondary' : 'outline'} className="text-xs">
                        {thread.lastMessage.ai_generated ? 'AI' : 'Customer'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Chat Messages */}
        <Card className="lg:col-span-2">
          {selectedThread ? (
            <>
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar>
                      <AvatarFallback className="bg-blue-100 text-blue-700">
                        {selectedThread.sender.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-medium text-slate-900">{selectedThread.sender}</h3>
                      <p className="text-sm text-slate-500">
                        {selectedThread.messages.length} messages
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-green-50 text-green-700">
                    Active
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[400px] p-4">
                  <div className="space-y-4">
                    {selectedThread.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${
                          message.ai_generated ? 'flex-row-reverse' : ''
                        }`}
                      >
                        <Avatar className="w-8 h-8 flex-shrink-0">
                          <AvatarFallback className={
                            message.ai_generated 
                              ? 'bg-purple-100 text-purple-700' 
                              : 'bg-blue-100 text-blue-700'
                          }>
                            {message.ai_generated ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                          </AvatarFallback>
                        </Avatar>
                        <div className={`flex-1 max-w-md ${message.ai_generated ? 'text-right' : ''}`}>
                          <div className={`p-3 rounded-lg ${
                            message.ai_generated
                              ? 'bg-purple-50 border border-purple-200'
                              : 'bg-slate-50 border border-slate-200'
                          }`}>
                            <p className="text-sm text-slate-900">{message.text}</p>
                            {message.context && (
                              <div className="mt-2 text-xs text-slate-500">
                                <p>Context: {JSON.stringify(message.context)}</p>
                              </div>
                            )}
                          </div>
                          <div className={`flex items-center gap-2 mt-1 text-xs text-slate-400 ${
                            message.ai_generated ? 'justify-end' : ''
                          }`}>
                            <span>
                              {new Date(message.ts).toLocaleTimeString('en-US', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                            {message.ai_generated && (
                              <span>• {message.tokens_in + message.tokens_out} tokens</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="border-t p-4">
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder="Type a message to intervene..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1"
                    />
                    <Button onClick={handleSendMessage} disabled={!newMessage.trim()}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    AI agent will pause when you send a message. Press "Resume AI" to continue automation.
                  </p>
                </div>
              </CardContent>
            </>
          ) : (
            <CardContent className="flex items-center justify-center h-full">
              <div className="text-center">
                <MessageCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">Select a Conversation</h3>
                <p className="text-slate-500">
                  Choose a conversation from the list to view the chat history
                </p>
              </div>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
}
