import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MessageSquare, Search, Filter, Eye, AlertCircle, Loader2 } from 'lucide-react';
import { productionApi, Conversation } from '../services/productionApi';
import { Alert, AlertDescription } from '../components/ui/alert';

interface ConversationsState {
  conversations: Conversation[];
  isLoading: boolean;
  error: string | null;
  searchTerm: string;
  selectedConversation: Conversation | null;
}

export function Conversations() {
  const [state, setState] = useState<ConversationsState>({
    conversations: [],
    isLoading: true,
    error: null,
    searchTerm: '',
    selectedConversation: null
  });

  // Load conversations data from real API
  const loadConversations = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await productionApi.getConversations();
      
      if (response.error) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: `Failed to load conversations: ${response.error}` 
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        conversations: response.data || [],
        isLoading: false,
        error: null
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: 'Network error loading conversations' 
      }));
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Filter conversations based on search term
  const filteredConversations = state.conversations.filter(conversation =>
    conversation.text.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
    conversation.id.toString().includes(state.searchTerm)
  );

  // Calculate stats from real data
  const totalConversations = state.conversations.length;
  const aiResponses = state.conversations.filter(c => c.ai_generated).length;
  const customerMessages = state.conversations.filter(c => !c.ai_generated).length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'waiting': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Active';
      case 'waiting': return 'Waiting';
      case 'resolved': return 'Resolved';
      default: return status;
    }
  };

  // Loading state
  if (state.isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-slate-600">Loading conversations...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (state.error) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {state.error}
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-4"
              onClick={loadConversations}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Conversations</h1>
          <p className="text-slate-500 mt-1">
            Manage customer conversations and AI responses ({totalConversations} messages)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadConversations}>
            <Search className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {customerMessages > 0 && (
            <Badge variant="outline" className="bg-blue-50 text-blue-700">
              {customerMessages} customer messages
            </Badge>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="Search conversations..." 
            className="pl-10"
            value={state.searchTerm}
            onChange={(e) => setState(prev => ({ ...prev, searchTerm: e.target.value }))}
          />
        </div>
        <Button variant="outline" onClick={loadConversations}>
          <Filter className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Empty state when no conversations */}
      {filteredConversations.length === 0 && !state.isLoading ? (
        <Card className="p-12 text-center">
          <MessageSquare className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">
            {state.searchTerm ? 'No conversations found' : 'No conversations yet'}
          </h3>
          <p className="text-slate-500 mb-6">
            {state.searchTerm 
              ? `No conversations match "${state.searchTerm}". Try a different search term.`
              : 'Conversations will appear here when customers message you on Instagram.'
            }
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Conversations List
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y">
                {filteredConversations.map((conversation) => (
                  <div 
                    key={conversation.id}
                    className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${
                      state.selectedConversation?.id === conversation.id ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => setState(prev => ({ ...prev, selectedConversation: conversation }))}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-slate-900">
                            Message #{conversation.id}
                          </h3>
                          <Badge 
                            variant="outline"
                            className={conversation.ai_generated ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}
                          >
                            {conversation.ai_generated ? 'AI' : 'Customer'}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-600 mb-2 line-clamp-2">
                          {conversation.text}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500">
                            {new Date(conversation.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Conversation Details</CardTitle>
            </CardHeader>
            <CardContent>
              {state.selectedConversation ? (
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="font-semibold">Message #{state.selectedConversation.id}</h3>
                      <Badge 
                        variant="outline"
                        className={state.selectedConversation.ai_generated ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}
                      >
                        {state.selectedConversation.ai_generated ? 'AI Generated' : 'Customer Message'}
                      </Badge>
                    </div>
                    <p className="text-slate-800 mb-3">
                      {state.selectedConversation.text}
                    </p>
                    <p className="text-sm text-slate-500">
                      {new Date(state.selectedConversation.created_at).toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button size="sm">
                      Reply
                    </Button>
                    <Button size="sm" variant="outline">
                      Mark as Resolved
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <MessageSquare className="mx-auto h-12 w-12 text-slate-400 mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">
                    Select a conversation to view details
                  </h3>
                  <p className="text-slate-500">
                    Click on any conversation from the list to view messages and respond
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Real Statistics from API Data */}
      <Card>
        <CardHeader>
          <CardTitle>Conversation Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{totalConversations}</div>
              <div className="text-sm text-slate-500">Total Messages</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{aiResponses}</div>
              <div className="text-sm text-slate-500">AI Responses</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{customerMessages}</div>
              <div className="text-sm text-slate-500">Customer Messages</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-600">
                {totalConversations > 0 ? Math.round((aiResponses / totalConversations) * 100) : 0}%
              </div>
              <div className="text-sm text-slate-500">AI Response Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
