import type { KBDocument as KBDocumentType, Conversation as ConversationType } from '../types';
import axios, { AxiosInstance } from 'axios';

// DEBUG: Log environment variables at load time
console.log('DEBUG: ENVIRONMENT VARIABLES');
console.log('DEBUG: import.meta.env:', import.meta.env);
console.log('DEBUG: VITE_API_BASE_URL from env:', import.meta.env.VITE_API_BASE_URL);

// API Configuration - HARDCODED CORRECT URL
const API_BASE_URL = 'https://igshop-api.azurewebsites.net';
console.log('DEBUG: API_BASE_URL set to:', API_BASE_URL);

// Create axios instance with the correct base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

console.log('DEBUG: Axios instance baseURL:', api.defaults.baseURL);

// API Response types
interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status?: number;
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

// Catalog interfaces
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

// Order interfaces
interface Order {
  id: number;
  customer_name: string;
  customer: string;
  sku: string;
  total_amount: number;
  status: string;
  created_at: string;
}

// Analytics interfaces
interface Analytics {
  total_orders: number;
  pending_orders: number;
  confirmed_orders: number;
  total_products: number;
  total_revenue: number;
  top_products: CatalogItem[];
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
    this.api = api;

    // Add request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        
        // Handle 401 errors by clearing token
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Instagram OAuth
  async getInstagramAuthUrl(): Promise<ApiResponse<{ auth_url: string; state: string }>> {
    try {
      console.log('DEBUG: Making request to /auth/instagram/login...');
      console.log('DEBUG: API Base URL:', this.api.defaults.baseURL);
      console.log('DEBUG: Full URL will be:', `${this.api.defaults.baseURL}/auth/instagram/login`);
      
      const response = await this.api.get('/auth/instagram/login');
      
      console.log('SUCCESS: Instagram auth URL response:', response.data);
      return {
        data: response.data,
        status: response.status
      };
    } catch (error: any) {
      console.error('ERROR: Instagram auth URL error:', error);
      console.error('ERROR: Error message:', error.message);
      console.error('ERROR: Error response:', error.response?.data);
      console.error('ERROR: Request URL that failed:', error.config?.url);
      console.error('ERROR: Base URL used:', error.config?.baseURL);
      
      return {
        error: error.response?.data?.error || error.message || 'Failed to get Instagram authorization URL',
        status: error.response?.status || 500
      };
    }
  }

  // Handle Instagram callback
  async handleInstagramCallback(code: string, state: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.api.post('/auth/instagram/callback', {
        code,
        state
      });
      
      return {
        data: response.data,
        status: response.status
      };
    } catch (error: any) {
      console.error('Instagram callback error:', error);
      return {
        error: error.response?.data?.error || error.message || 'Instagram callback failed',
        status: error.response?.status || 500
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/health');
      return {
        data: response.data,
        status: response.status
      };
    } catch (error: any) {
      return {
        error: error.message,
        status: error.response?.status || 500
      };
    }
  }

  // Authentication methods
  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await this.api.post('/auth/register', data);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  async login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await this.api.post('/auth/login', data);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Catalog methods
  async getCatalog(): Promise<ApiResponse<CatalogItem[]>> {
    try {
      const response = await this.api.get('/catalog');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  async createCatalogItem(item: CreateCatalogItemRequest): Promise<ApiResponse<{ id: number; message: string; enhanced_description: string }>> {
    try {
      const response = await this.api.post('/catalog', item);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  async updateCatalogItem(itemId: number, item: Partial<CreateCatalogItemRequest>): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await this.api.put(`/catalog/${itemId}`, item);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  async deleteCatalogItem(itemId: number): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await this.api.delete(`/catalog/${itemId}`);
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Order methods
  async getOrders(): Promise<ApiResponse<Order[]>> {
    try {
      const response = await this.api.get('/orders');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  async updateOrderStatus(orderId: number, status: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await this.api.put(`/orders/${orderId}/status`, { status });
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // AI methods
  async testAIResponse(message: string): Promise<ApiResponse<AITestResponse>> {
    try {
      const response = await this.api.post('/ai/test-response', { message });
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Analytics
  async getDashboardAnalytics(): Promise<ApiResponse<Analytics>> {
    try {
      const response = await this.api.get('/analytics/dashboard');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Conversations
  async getConversations(): Promise<ApiResponse<ConversationApi[]>> {
    try {
      const response = await this.api.get('/conversations');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Knowledge Base
  async getKnowledgeBase(): Promise<ApiResponse<KBDocumentApi[]>> {
    try {
      const response = await this.api.get('/kb');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  // Utility methods
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.healthCheck();
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async verifyToken(): Promise<ApiResponse<{ valid: boolean }>> {
    try {
      const response = await this.api.get('/auth/verify');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.response?.data?.error || error.message };
    }
  }

  setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  clearAuthToken(): void {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }
}

// Create and export singleton instance
export const apiService = new ApiService();

// Export types
export type {
  ApiResponse,
  CatalogItem,
  CreateCatalogItemRequest,
  Order,
  Analytics,
  ConversationApi as Conversation,
  KBDocumentApi as KBDocument,
  AITestResponse,
  AuthResponse,
  LoginRequest,
  RegisterRequest
};

// Connection check utility
export const checkApiConnection = async (): Promise<boolean> => {
  try {
    const response = await apiService.testConnection();
    return response;
  } catch {
    return false;
  }
}; 