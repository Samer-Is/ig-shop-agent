/**
 * Production API Service - Updated to match backend
 * IG-Shop-Agent: Real backend integration
 */

// Use environment variable or fallback for API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://igshop-dev-yjhtoi-api.azurewebsites.net';

// Import types from main types file
import type { KBDocument as KBDocumentType, Conversation as ConversationType } from '../types';
import axios, { AxiosInstance } from 'axios';

// API Response types matching Flask backend
interface ApiResponse<T = any> {
  data?: T;
  error?: string;
}

// Authentication interfaces
interface InstagramAuthResponse {
  auth_url: string;
  state: string;
}

interface InstagramCallbackResponse {
  token: string;
  user: {
    id: number;
    instagram_handle: string;
    instagram_connected: boolean;
  };
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
  sku: string;
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

export class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true  // Important for cookies
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error);
        return Promise.reject(error);
      }
    );
  }

  // Instagram OAuth
  async getInstagramAuthUrl(): Promise<ApiResponse<{ auth_url: string; state: string }>> {
    try {
      const response = await this.api.get('/auth/instagram/login');
      const data = response.data;
      
      if (!data?.auth_url || !data?.state) {
        throw new Error('Invalid response: missing auth_url or state');
      }
      
      return { data };
    } catch (error: any) {
      console.error('Failed to get Instagram auth URL:', error);
      
      // Handle specific error cases
      if (error.response?.status === 500 && error.response?.data?.detail) {
        return { 
          error: error.response.data.detail 
        };
      }
      
      // Handle network errors
      if (error.code === 'ECONNABORTED' || !error.response) {
        return { 
          error: 'Network error: Please check your internet connection and try again.' 
        };
      }
      
      // Default error
      return { 
        error: 'Failed to get Instagram authorization URL. Please try again later.' 
      };
    }
  }

  async handleInstagramCallback(code: string, state: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.api.post('/auth/instagram/callback', { code, state });
      return { data: response.data };
    } catch (error: any) {
      console.error('Instagram callback error:', error);
      
      // Handle specific error cases
      if (error.response?.status === 400) {
        return { 
          error: error.response.data.detail || 'Invalid authentication request. Please try again.' 
        };
      }
      
      if (error.response?.status === 500) {
        return { 
          error: error.response.data.detail || 'Server error during authentication. Please try again later.' 
        };
      }
      
      // Handle network errors
      if (error.code === 'ECONNABORTED' || !error.response) {
        return { 
          error: 'Network error: Please check your internet connection and try again.' 
        };
      }
      
      // Default error
      return { 
        error: 'Failed to complete Instagram authentication. Please try again.' 
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/health');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.detail || 'API health check failed' };
    }
  }

  // Authentication - Updated to match backend
  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await this.api.post('/auth/register', data);
    if (response.data?.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response;
  }

  async login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await this.api.post('/auth/login', data);
    if (response.data?.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response;
  }

  // Catalog Management - Updated to match backend
  async getCatalog(): Promise<ApiResponse<CatalogItem[]>> {
    const response = await this.api.get('/api/catalog');
    return response;
  }

  async createCatalogItem(item: CreateCatalogItemRequest): Promise<ApiResponse<{ id: number; message: string; enhanced_description: string }>> {
    const response = await this.api.post('/api/catalog', item);
    return response;
  }

  async updateCatalogItem(itemId: number, item: Partial<CreateCatalogItemRequest>): Promise<ApiResponse<{ message: string }>> {
    const response = await this.api.put(`/api/catalog/${itemId}`, item);
    return response;
  }

  async deleteCatalogItem(itemId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await this.api.delete(`/api/catalog/${itemId}`);
    return response;
  }

  // Order Management - Updated to match backend
  async getOrders(): Promise<ApiResponse<Order[]>> {
    const response = await this.api.get('/api/orders');
    return response;
  }

  async updateOrderStatus(orderId: number, status: string): Promise<ApiResponse<{ message: string }>> {
    const response = await this.api.put(`/api/orders/${orderId}/status`, { status });
    return response;
  }

  // AI Agent - Updated to match backend
  async testAIResponse(message: string): Promise<ApiResponse<AITestResponse>> {
    const response = await this.api.post('/api/ai/chat', { message });
    return response;
  }

  // Analytics - Updated to match backend
  async getDashboardAnalytics(): Promise<ApiResponse<Analytics>> {
    const response = await this.api.get('/api/analytics');
    return response;
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
    if (!localStorage.getItem('auth_token')) {
      return { data: { valid: false }, status: 200 };
    }
    
    const response = await this.healthCheck();
    return { data: { valid: response.status === 200 }, status: response.status };
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
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