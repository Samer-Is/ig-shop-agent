const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://igshop-dev-yjhtoi-api.azurewebsites.net'  // Python Flask Azure Web App
  : 'http://localhost:8000';  // Local Flask app

// Import types from main types file
import type { KBDocument, Conversation } from '../types';

// API Response types matching Flask backend
interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Authentication interfaces
interface InstagramAuthResponse {
  auth_url: string;
  state: string;
}

interface InstagramCallbackResponse {
  success: boolean;
  session_token: string;
  tenant_id: string;
  user: {
    id: string;
    username: string;
    name: string;
  };
  instagram_accounts: Array<{
    id: string;
    username: string;
    name: string;
  }>;
}

interface TokenVerifyResponse {
  valid: boolean;
  user_id: string;
  username: string;
  tenant_id: string;
}

// Catalog interfaces - matching database schema
interface CatalogItem {
  id: string;
  tenant_id: string;
  sku: string;
  name: string;
  price_jod: number;
  media_url: string;
  extras: Record<string, any>;
  description?: string;
  category?: string;
  stock_quantity?: number;
  created_at: string;
  updated_at: string;
}

interface CatalogResponse {
  items: CatalogItem[];
  total: number;
  limit: number;
  offset: number;
}

interface CreateCatalogItemRequest {
  sku: string;
  name: string;
  price_jod: number;
  description?: string;
  category?: string;
  stock_quantity?: number;
  media_url?: string;
}

// Order interfaces - matching database schema
interface Order {
  id: string;
  tenant_id: string;
  sku: string;
  qty: number;
  customer: string;
  phone: string;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  created_at: string;
  updated_at: string;
  delivery_address?: string;
  notes?: string;
}

interface OrdersResponse {
  orders: Order[];
  total: number;
  limit: number;
  offset: number;
}

interface CreateOrderRequest {
  sku: string;
  qty: number;
  customer: string;
  phone: string;
  total_amount: number;
  delivery_address?: string;
  notes?: string;
}

// AI interfaces
interface AITestRequest {
  message: string;
}

interface AITestResponse {
  success: boolean;
  response: string;
  processed_at: string;
}

// Analytics interfaces
interface DashboardAnalytics {
  total_orders: number;
  total_revenue: number;
  total_products: number;
  pending_orders: number;
  confirmed_orders: number;
  recent_orders: Order[];
  top_products: CatalogItem[];
}

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage
    this.authToken = localStorage.getItem('ig_session_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const defaultHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

      // Add auth token if available
      if (this.authToken) {
        defaultHeaders['Authorization'] = `Bearer ${this.authToken}`;
      }

      const response = await fetch(url, {
        headers: { ...defaultHeaders, ...options.headers },
        ...options,
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = await response.text();
      }

      return {
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || data || 'Request failed',
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Set auth token
  setAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('ig_session_token', token);
  }

  // Clear auth token
  clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('ig_session_token');
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; service: string; version: string }>> {
    return this.request('/health');
  }

  async detailedHealthCheck(): Promise<ApiResponse<any>> {
    return this.request('/api/health');
  }

  // Authentication
  async getInstagramAuthUrl(businessName: string = '', redirectUri: string = ''): Promise<ApiResponse<InstagramAuthResponse>> {
    const params = new URLSearchParams();
    if (businessName) params.append('business_name', businessName);
    if (redirectUri) params.append('redirect_uri', redirectUri);
    
    return this.request(`/auth/instagram?${params.toString()}`);
  }

  async handleInstagramCallback(code: string, state: string, redirectUri: string = ''): Promise<ApiResponse<InstagramCallbackResponse>> {
    const params = new URLSearchParams({ code, state });
    if (redirectUri) params.append('redirect_uri', redirectUri);
    
    return this.request(`/auth/callback?${params.toString()}`);
  }

  async verifyToken(): Promise<ApiResponse<TokenVerifyResponse>> {
    return this.request('/auth/verify', { method: 'POST' });
  }

  // Catalog Management
  async getCatalog(limit: number = 50, offset: number = 0, category?: string, search?: string): Promise<ApiResponse<CatalogResponse>> {
    const params = new URLSearchParams({ 
      limit: limit.toString(), 
      offset: offset.toString() 
    });
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    
    return this.request(`/api/catalog?${params.toString()}`);
  }

  async createCatalogItem(item: CreateCatalogItemRequest): Promise<ApiResponse<{ success: boolean; item_id: string; message: string }>> {
    return this.request('/api/catalog', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async updateCatalogItem(itemId: string, item: Partial<CreateCatalogItemRequest>): Promise<ApiResponse<{ success: boolean; message: string }>> {
    return this.request(`/api/catalog/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  }

  async deleteCatalogItem(itemId: string): Promise<ApiResponse<{ success: boolean; message: string }>> {
    return this.request(`/api/catalog/${itemId}`, {
      method: 'DELETE',
    });
  }

  // Order Management
  async getOrders(limit: number = 50, offset: number = 0, status?: string): Promise<ApiResponse<OrdersResponse>> {
    const params = new URLSearchParams({ 
      limit: limit.toString(), 
      offset: offset.toString() 
    });
    if (status) params.append('status', status);
    
    return this.request(`/api/orders?${params.toString()}`);
  }

  async createOrder(order: CreateOrderRequest): Promise<ApiResponse<{ success: boolean; order_id: string; message: string }>> {
    return this.request('/api/orders', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async updateOrderStatus(orderId: string, status: string): Promise<ApiResponse<{ success: boolean; message: string }>> {
    return this.request(`/api/orders/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  // AI Agent
  async testAIResponse(message: string): Promise<ApiResponse<AITestResponse>> {
    return this.request('/api/ai/test-response', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Analytics
  async getDashboardAnalytics(): Promise<ApiResponse<DashboardAnalytics>> {
    return this.request('/api/analytics/dashboard');
  }

  // Knowledge Base
  async getKnowledgeBase(): Promise<KBDocument[]> {
    const response = await this.request<{ documents: KBDocument[] }>('/api/knowledge-base');
    return response.data?.documents || [];
  }

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    const response = await this.request<{ conversations: Conversation[] }>('/api/conversations');
    return response.data?.conversations || [];
  }

  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.healthCheck();
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export types
export type {
  ApiResponse,
  InstagramAuthResponse,
  InstagramCallbackResponse,
  TokenVerifyResponse,
  CatalogItem,
  CatalogResponse,
  CreateCatalogItemRequest,
  Order,
  OrdersResponse,
  CreateOrderRequest,
  AITestRequest,
  AITestResponse,
  DashboardAnalytics,
};

// Utility function to check if API is available
export const checkApiConnection = async (): Promise<boolean> => {
  return await apiService.testConnection();
}; 