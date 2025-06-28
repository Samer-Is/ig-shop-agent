// React imports for hooks
import { useState, useEffect } from 'react';

// Real API Service that connects to the working backend
const API_BASE_URL = 'https://igshop-dev-functions-v2.azurewebsites.net/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

interface BackendProduct {
  id: string;
  name: string;
  name_en: string;
  price: number;
  currency: string;
  description: string;
  description_en: string;
  image_url: string;
  in_stock: boolean;
  stock_quantity: number;
  category: string;
}

interface BackendAnalytics {
  total_messages: number;
  total_orders: number;
  response_rate: number;
  conversion_rate: number;
  revenue_today: number;
  ai_cost_today: number;
}

interface BackendCustomer {
  customer_id: string;
  name: string;
  last_message: string;
  last_interaction: string;
  message_count: number;
  orders_count: number;
}

class RealApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      console.log(`API Request: ${url}`); // For debugging
      
      const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

      const response = await fetch(url, {
        headers: { ...defaultHeaders, ...options.headers },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`API Response for ${endpoint}:`, data); // For debugging

      return {
        data,
        success: true,
      };
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      return {
        error: error instanceof Error ? error.message : 'Network error',
        success: false,
      };
    }
  }

  // Health check
  async healthCheck() {
    return this.request<{ status: string; version: string; message: string }>('/health');
  }

  // Get product catalog
  async getProducts() {
    return this.request<{ products: BackendProduct[]; total: number }>('/catalog');
  }

  // Get analytics data
  async getAnalytics() {
    return this.request<BackendAnalytics>('/analytics');
  }

  // Get recent messages
  async getRecentMessages() {
    return this.request<{ messages: any[]; total: number }>('/messages/recent');
  }

  // Get customer list
  async getCustomers() {
    return this.request<{ customers: BackendCustomer[]; total: number }>('/customers');
  }

  // Test AI agent
  async testAiAgent(message: string) {
    return this.request<{ ai_response: string; detected_language: string; intent: string }>('/ai/test-response', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Instagram connection status
  async getInstagramStatus() {
    return this.request<{ connected: boolean; page_info?: any }>('/instagram/status');
  }

  // Connect to Instagram
  async connectInstagram(code: string) {
    return this.request<{ success: boolean; access_token?: string }>('/instagram/oauth/callback', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  // Disconnect Instagram
  async disconnectInstagram() {
    return this.request<{ success: boolean }>('/instagram/disconnect', {
      method: 'POST',
    });
  }

  // Test connection
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.healthCheck();
      return response.success;
    } catch {
      return false;
    }
  }
}

// Create singleton instance
export const realApiService = new RealApiService();

// Export types
export type {
  ApiResponse,
  BackendProduct,
  BackendAnalytics,
  BackendCustomer,
};

// Connection status hook
export const useApiConnection = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      setIsLoading(true);
      const connected = await realApiService.testConnection();
      setIsConnected(connected);
      setIsLoading(false);
    };

    checkConnection();
    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  return { isConnected, isLoading };
}; 