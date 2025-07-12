import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface AnalyticsData {
  orders: {
    total: number;
    revenue: number;
    average_value: number;
    pending: number;
    completed: number;
  };
  catalog: {
    total_products: number;
    active_products: number;
    out_of_stock: number;
  };
  conversations: {
    total_messages: number;
    ai_responses: number;
    customer_messages: number;
  };
}

interface Product {
  id: string;
  name: string;
  description: string;
  price_jod: number;
  stock_quantity: number;
  status: string;
  product_link?: string;
}

interface Conversation {
  id: string;
  customer: string;
  message: string;
  is_ai_response: boolean;
  created_at: string;
}

interface BusinessRules {
  working_hours: string;
  terms_conditions: string;
  custom_prompt: string;
  ai_instructions: string;
}

interface KnowledgeBaseItem {
  id: string;
  title: string;
  content: string;
  type: 'document' | 'link' | 'text';
  created_at: string;
}

const MinimalDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [businessRules, setBusinessRules] = useState<BusinessRules>({
    working_hours: '9:00 AM - 6:00 PM',
    terms_conditions: 'Standard terms and conditions',
    custom_prompt: 'You are a helpful shop assistant.',
    ai_instructions: 'Be polite and helpful. Answer in Arabic or English based on customer language.'
  });
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [testMessage, setTestMessage] = useState('');
  const [aiTestResult, setAiTestResult] = useState('');
  const [aiTestError, setAiTestError] = useState('');
  const [isTestingAI, setIsTestingAI] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [analyticsData, productsData, conversationsData] = await Promise.all([
        apiService.getDashboardAnalytics(),
        apiService.getCatalog(),
        apiService.getConversations()
      ]);

      setAnalytics(analyticsData.data);
      setProducts(productsData.data || []);
      setConversations((conversationsData.data || []).slice(0, 10)); // Last 10 conversations
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProduct = async (productId: string, updates: Partial<Product>) => {
    try {
      // In a real implementation, this would call the API
      setProducts(prev => prev.map(p => p.id === productId ? {...p, ...updates} : p));
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const addNewProduct = async () => {
    const newProduct: Product = {
      id: Date.now().toString(), // Temporary ID
      name: 'New Product',
      description: 'Product description',
      price_jod: 10.0,
      stock_quantity: 1,
      status: 'active'
    };
    
    setProducts(prev => [...prev, newProduct]);
    
    // TODO: Call API to add product to backend
    console.log('Adding new product:', newProduct);
  };

  const saveBusinessRules = async () => {
    try {
      // In a real implementation, this would call the API
      alert('Business rules saved successfully!');
    } catch (error) {
      console.error('Error saving business rules:', error);
    }
  };

  const testAI = async () => {
    if (!testMessage.trim()) return;
    
    setIsTestingAI(true);
    setAiTestResult('');
    setAiTestError('');
    
    try {
      const response = await apiService.testAIResponse(
        testMessage, 
        businessRules, 
        products,
        knowledgeBase
      );
      
      if (response.error) {
        setAiTestError(response.error);
      } else {
        setAiTestResult(response.data?.response || 'No response received');
      }
    } catch (error) {
      setAiTestError('Failed to test AI: ' + error);
    } finally {
      setIsTestingAI(false);
    }
  };

  const addKnowledgeItem = (type: 'document' | 'link' | 'text') => {
    const newItem: KnowledgeBaseItem = {
      id: Date.now().toString(),
      title: '',
      content: '',
      type,
      created_at: new Date().toISOString()
    };
    setKnowledgeBase(prev => [...prev, newItem]);
  };

  const updateKnowledgeItem = (id: string, updates: Partial<KnowledgeBaseItem>) => {
    setKnowledgeBase(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ));
  };

  const deleteKnowledgeItem = (id: string) => {
    setKnowledgeBase(prev => prev.filter(item => item.id !== id));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const newItem: KnowledgeBaseItem = {
        id: Date.now().toString(),
        title: file.name,
        content: content,
        type: 'document',
        created_at: new Date().toISOString()
      };
      setKnowledgeBase(prev => [...prev, newItem]);
    };
    reader.readAsText(file);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Simple Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">IG Shop Dashboard</h1>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="border-b">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'products', label: 'Products' },
              { id: 'knowledge', label: 'Knowledge Base' },
              { id: 'rules', label: 'Business Rules' },
              { id: 'ai-test', label: 'AI Test' },
              { id: 'conversations', label: 'Conversations' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Orders Analytics */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Orders</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Total Orders:</span>
                  <span className="font-bold">{analytics.orders.total}</span>
                </div>
                <div className="flex justify-between">
                  <span>Revenue:</span>
                  <span className="font-bold">{analytics.orders.revenue} JOD</span>
                </div>
                <div className="flex justify-between">
                  <span>Pending:</span>
                  <span className="text-orange-600 font-bold">{analytics.orders.pending}</span>
                </div>
                <div className="flex justify-between">
                  <span>Completed:</span>
                  <span className="text-green-600 font-bold">{analytics.orders.completed}</span>
                </div>
              </div>
            </div>

            {/* Products Analytics */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Products</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Total Products:</span>
                  <span className="font-bold">{analytics.catalog.total_products}</span>
                </div>
                <div className="flex justify-between">
                  <span>Active:</span>
                  <span className="text-green-600 font-bold">{analytics.catalog.active_products}</span>
                </div>
                <div className="flex justify-between">
                  <span>Out of Stock:</span>
                  <span className="text-red-600 font-bold">{analytics.catalog.out_of_stock}</span>
                </div>
              </div>
            </div>

            {/* Conversations Analytics */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Conversations</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Total Messages:</span>
                  <span className="font-bold">{analytics.conversations.total_messages}</span>
                </div>
                <div className="flex justify-between">
                  <span>AI Responses:</span>
                  <span className="text-blue-600 font-bold">{analytics.conversations.ai_responses}</span>
                </div>
                <div className="flex justify-between">
                  <span>Customer Messages:</span>
                  <span className="text-gray-600 font-bold">{analytics.conversations.customer_messages}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Products Tab */}
        {activeTab === 'products' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">Product Catalog</h3>
              <button
                onClick={addNewProduct}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
              >
                <span className="mr-2">+</span>
                Add Product
              </button>
            </div>
            <div className="p-6">
              {products.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-lg mb-2">No products yet</p>
                  <p>Click "Add Product" to create your first product</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {products.map(product => (
                  <div key={product.id} className="border rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Name</label>
                        <input
                          type="text"
                          value={product.name}
                          onChange={(e) => updateProduct(product.id, { name: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Price (JOD)</label>
                        <input
                          type="number"
                          value={product.price_jod}
                          onChange={(e) => updateProduct(product.id, { price_jod: parseFloat(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Stock</label>
                        <input
                          type="number"
                          value={product.stock_quantity}
                          onChange={(e) => updateProduct(product.id, { stock_quantity: parseInt(e.target.value) })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <select
                          value={product.status}
                          onChange={(e) => updateProduct(product.id, { status: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        >
                          <option value="active">Active</option>
                          <option value="inactive">Inactive</option>
                        </select>
                      </div>
                    </div>
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        value={product.description}
                        onChange={(e) => updateProduct(product.id, { description: e.target.value })}
                        rows={2}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                    </div>
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700">Product Link (URL)</label>
                      <input
                        type="url"
                        value={product.product_link || ''}
                        onChange={(e) => updateProduct(product.id, { product_link: e.target.value })}
                        placeholder="https://example.com/product-page"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                    </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Knowledge Base Tab */}
        {activeTab === 'knowledge' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Knowledge Base</h3>
              <p className="text-gray-600 mt-2">Upload documents, add website links, and create text content for your AI to reference</p>
            </div>
            <div className="p-6">
              {/* Action Buttons */}
              <div className="flex space-x-4 mb-6">
                <button
                  onClick={() => addKnowledgeItem('text')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Add Text Content
                </button>
                <button
                  onClick={() => addKnowledgeItem('link')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  Add Website Link
                </button>
                <label className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 cursor-pointer">
                  Upload Document
                  <input
                    type="file"
                    accept=".txt,.pdf,.doc,.docx"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Knowledge Items */}
              <div className="space-y-4">
                {knowledgeBase.map(item => (
                  <div key={item.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          item.type === 'document' ? 'bg-purple-100 text-purple-800' :
                          item.type === 'link' ? 'bg-green-100 text-green-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {item.type.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <button
                        onClick={() => deleteKnowledgeItem(item.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                        <input
                          type="text"
                          value={item.title}
                          onChange={(e) => updateKnowledgeItem(item.id, { title: e.target.value })}
                          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                          placeholder="Enter a descriptive title..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {item.type === 'link' ? 'URL' : 'Content'}
                        </label>
                        {item.type === 'link' ? (
                          <input
                            type="url"
                            value={item.content}
                            onChange={(e) => updateKnowledgeItem(item.id, { content: e.target.value })}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder="https://example.com"
                          />
                        ) : (
                          <textarea
                            value={item.content}
                            onChange={(e) => updateKnowledgeItem(item.id, { content: e.target.value })}
                            rows={item.type === 'document' ? 8 : 4}
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            placeholder={item.type === 'document' ? 'Document content will appear here...' : 'Enter your text content...'}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {knowledgeBase.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <p>No knowledge base items yet.</p>
                    <p className="text-sm mt-2">Add documents, links, or text content to help your AI provide better responses.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* AI Test Tab */}
        {activeTab === 'ai-test' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">AI Test Playground</h3>
              <p className="text-gray-600 mt-2">Test your AI assistant with full context (products, business rules, etc.)</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Test Message</label>
                  <textarea
                    value={testMessage}
                    onChange={(e) => setTestMessage(e.target.value)}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Type a customer message to test how your AI would respond..."
                  />
                </div>
                
                <button
                  onClick={testAI}
                  disabled={!testMessage.trim() || isTestingAI}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isTestingAI ? 'Testing...' : 'Test AI Response'}
                </button>
                
                {aiTestResult && (
                  <div className="mt-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                    <h4 className="font-medium text-blue-900 mb-2">AI Response:</h4>
                    <p className="text-blue-800">{aiTestResult}</p>
                  </div>
                )}
                
                {aiTestError && (
                  <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
                    <h4 className="font-medium text-red-900 mb-2">Error:</h4>
                    <p className="text-red-800">{aiTestError}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Business Rules Tab */}
        {activeTab === 'rules' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Business Rules & AI Settings</h3>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Working Hours</label>
                <input
                  type="text"
                  value={businessRules.working_hours}
                  onChange={(e) => setBusinessRules(prev => ({ ...prev, working_hours: e.target.value }))}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Terms & Conditions</label>
                <textarea
                  value={businessRules.terms_conditions}
                  onChange={(e) => setBusinessRules(prev => ({ ...prev, terms_conditions: e.target.value }))}
                  rows={4}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Custom AI Prompt</label>
                <textarea
                  value={businessRules.custom_prompt}
                  onChange={(e) => setBusinessRules(prev => ({ ...prev, custom_prompt: e.target.value }))}
                  rows={3}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="Define how your AI assistant should behave..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">AI Instructions</label>
                <textarea
                  value={businessRules.ai_instructions}
                  onChange={(e) => setBusinessRules(prev => ({ ...prev, ai_instructions: e.target.value }))}
                  rows={4}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="Specific instructions for handling customer inquiries..."
                />
              </div>

              <button
                onClick={saveBusinessRules}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
              >
                Save Business Rules
              </button>
            </div>
          </div>
        )}

        {/* Conversations Tab */}
        {activeTab === 'conversations' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Recent Conversations</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {conversations.map(conversation => (
                  <div
                    key={conversation.id}
                    className={`p-4 rounded-lg ${
                      conversation.is_ai_response
                        ? 'bg-blue-50 border-l-4 border-blue-500'
                        : 'bg-gray-50 border-l-4 border-gray-500'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium">
                        {conversation.is_ai_response ? 'AI Assistant' : `Customer ${conversation.customer}`}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(conversation.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-gray-700">{conversation.message}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MinimalDashboard; 