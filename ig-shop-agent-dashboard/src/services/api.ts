/**
 * Production API Service - Updated to match backend
 * IG-Shop-Agent: Real backend integration
 */

// Use the production backend URL
const API_BASE_URL = 'https://igshop-api.azurewebsites.net';

// Import types from main types file
import type { KBDocument as KBDocumentType, Conversation as ConversationType } from '../types';

// API Response types matching Flask backend
interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Authentication interfaces
interface InstagramAuthResponse {
  auth_url: string;
  status: string;
}

interface InstagramCallbackResponse {
  message: string;
  instagram_username: string;
  status: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  business_name?: string;
}

interface AuthResponse {
  message: string;
  token: string;
  user: {
    id: number;
    email: string;
    business_name: string;
    instagram_connected?: boolean;
  };
}

// Catalog interfaces - matching database schema
interface CatalogItem {
  id: number;
  name: string;
  description: string;
  price_jod: number;
  category: string;
  image_url?: string;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
}

interface CreateCatalogItemRequest {
  name: string;
  description?: string;
  price_jod: number;
  category?: string;
  stock_quantity?: number;
  image_url?: string;
}

// Order interfaces - matching database schema
interface Order {
  id: number;
  customer_name: string;
  customer: string;     // Alternative property name used in some components
  sku: string;          // Missing SKU property
  total_amount: number;
  status: string;
  created_at: string;
}

// Analytics interfaces
interface Analytics {
  // Flat properties expected by frontend
  total_orders: number;
  pending_orders: number;
  confirmed_orders: number;
  total_products: number;
  total_revenue: number;
  top_products: CatalogItem[];  // Missing property
  
  // Nested structures for additional data
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
  recent_orders: Order[];
}

interface ConversationApi {
  id: number;
  text: string;
  ai_generated: boolean;
  created_at: string;
}

interface KBDocumentApi {
  id: number;
  title: string;
  file_uri: string;
}

interface AITestResponse {
  response: string;
  intent_analysis: {
    intent: string;
    products_mentioned: string[];
    urgency: string;
    language: string;
  };
  catalog_items_used: number;
}

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Try to get token from localStorage
    this.authToken = localStorage.getItem('access_token');
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
    localStorage.setItem('access_token', token);
  }

  // Clear auth token
  clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('access_token');
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<any>> {
    return this.request('/health');
  }

  // Authentication - Updated to match backend
  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (response.data?.token) {
      this.setAuthToken(response.data.token);
    }

    return response;
  }

  // Instagram OAuth - Updated to match backend
  async getInstagramAuthUrl(): Promise<ApiResponse<InstagramAuthResponse>> {
    return this.request('/auth/instagram');
  }

  // This method handles the callback differently since backend handles it directly
  async handleInstagramCallback(code: string, state: string): Promise<ApiResponse<InstagramCallbackResponse>> {
    // The backend handles this automatically via /auth/instagram/callback
    // This is just for the frontend to know the result
    return { data: { message: 'Handled by backend', instagram_username: '', status: 'success' }, status: 200 };
  }

  // Catalog Management - Updated to match backend
  async getCatalog(): Promise<ApiResponse<CatalogItem[]>> {
    return this.request('/api/catalog');
  }

  async createCatalogItem(item: CreateCatalogItemRequest): Promise<ApiResponse<{ id: number; message: string; enhanced_description: string }>> {
    return this.request('/api/catalog', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async updateCatalogItem(itemId: number, item: Partial<CreateCatalogItemRequest>): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/catalog/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  }

  async deleteCatalogItem(itemId: number): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/catalog/${itemId}`, {
      method: 'DELETE',
    });
  }

  // Order Management - Updated to match backend
  async getOrders(): Promise<ApiResponse<Order[]>> {
    return this.request('/api/orders');
  }

  async updateOrderStatus(orderId: number, status: string): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/orders/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  // AI Agent - Updated to match backend
  async testAIResponse(message: string): Promise<ApiResponse<AITestResponse>> {
    return this.request('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Analytics - Updated to match backend
  async getDashboardAnalytics(): Promise<ApiResponse<Analytics>> {
    return this.request('/api/analytics');
  }

  // Knowledge Base - Placeholder (not implemented in backend yet)
  async getKnowledgeBase(): Promise<KBDocumentApi[]> {
    // Backend doesn't have this endpoint yet, return empty
    return [];
  }

  // Conversations - Placeholder (not implemented in backend yet)
  async getConversations(): Promise<ConversationApi[]> {
    // Backend doesn't have this endpoint yet, return empty
    return [];
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

  // Additional methods to match frontend usage
  async verifyToken(): Promise<ApiResponse<{ valid: boolean }>> {
    if (!this.authToken) {
      return { data: { valid: false }, status: 200 };
    }
    
    const response = await this.request('/health');
    return { data: { valid: response.status === 200 }, status: response.status };
  }

  isAuthenticated(): boolean {
    return !!this.authToken;
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export types
export type {
  ApiResponse,
  InstagramAuthResponse,
  InstagramCallbackResponse,
  AuthResponse,
  CatalogItem,
  CreateCatalogItemRequest,
  Order,
  Analytics,
  Analytics as DashboardAnalytics,
  AITestResponse,
};

// Utility function to check if API is available
export const checkApiConnection = async (): Promise<boolean> => {
  return await apiService.testConnection();
}; 