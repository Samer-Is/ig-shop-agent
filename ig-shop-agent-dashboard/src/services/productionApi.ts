/**
 * Production API Service - 100% Complete
 * IG-Shop-Agent: Enterprise SaaS Platform
 */

// Production API base URL - Python Flask Backend
const API_BASE_URL = 'https://igshop-api.azurewebsites.net';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface CatalogItem {
  id: number;
  name: string;
  description: string;
  price_jod: number;
  category: string;
  image_url?: string;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  customer_name: string;
  total_amount: number;
  status: string;
  instagram_message_id?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  product_name: string;
  quantity: number;
  price: number;
}

export interface Analytics {
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

export interface Conversation {
  id: number;
  text: string;
  ai_generated: boolean;
  created_at: string;
}

export interface AIResponse {
  response: string;
  intent_analysis: {
    intent: string;
    products_mentioned: string[];
    urgency: string;
    language: string;
  };
  catalog_items_used: number;
}

class ProductionApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      
      const defaultHeaders: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (this.token) {
        defaultHeaders.Authorization = `Bearer ${this.token}`;
      }

      const config: RequestInit = {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      };

      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
          return { error: 'Authentication expired' };
        }
        
        const errorData = await response.json().catch(() => ({}));
        return { error: errorData.error || `HTTP Error: ${response.status}` };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  // Authentication
  async authenticateWithInstagram(code: string): Promise<ApiResponse<{ access_token: string; user: any }>> {
    const response = await this.request<{ access_token: string; user: any }>('/api/auth/instagram', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });

    if (response.data) {
      this.token = response.data.access_token;
      localStorage.setItem('access_token', this.token);
    }

    return response;
  }

  // Health check
  async checkHealth(): Promise<ApiResponse<any>> {
    return this.request('/health');
  }

  // Catalog operations
  async getCatalog(): Promise<ApiResponse<CatalogItem[]>> {
    return this.request<CatalogItem[]>('/api/catalog');
  }

  async addCatalogItem(item: Partial<CatalogItem>): Promise<ApiResponse<{ id: number; message: string; enhanced_description: string }>> {
    return this.request('/api/catalog', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async updateCatalogItem(id: number, item: Partial<CatalogItem>): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/catalog/${id}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    });
  }

  async deleteCatalogItem(id: number): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/catalog/${id}`, {
      method: 'DELETE',
    });
  }

  // Order operations
  async getOrders(): Promise<ApiResponse<Order[]>> {
    return this.request<Order[]>('/api/orders');
  }

  async getOrder(id: number): Promise<ApiResponse<Order>> {
    return this.request<Order>(`/api/orders/${id}`);
  }

  async updateOrderStatus(id: number, status: string): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/orders/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  // AI operations
  async generateAIResponse(message: string): Promise<ApiResponse<AIResponse>> {
    return this.request<AIResponse>('/api/ai/response', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Analytics
  async getAnalytics(): Promise<ApiResponse<Analytics>> {
    return this.request<Analytics>('/api/analytics');
  }

  // Conversations
  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    return this.request<Conversation[]>('/api/conversations');
  }

  // Business Profile operations
  async getBusinessProfile(): Promise<ApiResponse<any>> {
    return this.request('/api/profile');
  }

  async updateBusinessProfile(profile: any): Promise<ApiResponse<{ message: string }>> {
    return this.request('/api/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  // Knowledge Base operations
  async getKnowledgeBase(): Promise<ApiResponse<any[]>> {
    return this.request('/api/knowledge-base');
  }

  async uploadDocument(file: File): Promise<ApiResponse<{ message: string; id: number }>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/api/knowledge-base/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type, let browser set it for FormData
        Authorization: `Bearer ${this.token}`,
      },
    });
  }

  // Settings operations
  async getSettings(): Promise<ApiResponse<any>> {
    return this.request('/api/settings');
  }

  async updateSettings(settings: any): Promise<ApiResponse<{ message: string }>> {
    return this.request('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Instagram integration
  async getInstagramProfile(): Promise<ApiResponse<any>> {
    return this.request('/api/instagram/profile');
  }

  async refreshInstagramToken(): Promise<ApiResponse<{ message: string }>> {
    return this.request('/api/instagram/refresh-token', {
      method: 'POST',
    });
  }

  // Webhook operations
  async getWebhookStatus(): Promise<ApiResponse<{ status: string; last_activity: string }>> {
    return this.request('/api/webhook/status');
  }

  // Utility methods
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Retry mechanism for failed requests
  async retryRequest<T>(
    requestFn: () => Promise<ApiResponse<T>>, 
    maxRetries: number = 3
  ): Promise<ApiResponse<T>> {
    let lastError: string = '';
    
    for (let i = 0; i < maxRetries; i++) {
      const result = await requestFn();
      
      if (result.data) {
        return result;
      }
      
      lastError = result.error || 'Unknown error';
      
      // Wait before retrying (exponential backoff)
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
      }
    }
    
    return { error: `Failed after ${maxRetries} attempts: ${lastError}` };
  }

  // Batch operations
  async batchUpdateCatalog(updates: Array<{ id: number; data: Partial<CatalogItem> }>): Promise<ApiResponse<{ updated: number; errors: any[] }>> {
    return this.request('/api/catalog/batch', {
      method: 'PUT',
      body: JSON.stringify({ updates }),
    });
  }

  // Export data
  async exportData(type: 'catalog' | 'orders' | 'analytics'): Promise<ApiResponse<{ download_url: string }>> {
    return this.request(`/api/export/${type}`, {
      method: 'POST',
    });
  }
}

// Global instance
export const productionApi = new ProductionApiService();

// Export types and service
export default ProductionApiService; 