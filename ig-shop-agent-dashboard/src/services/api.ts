const API_BASE_URL = 'https://igshop-api.azurewebsites.net';

// API Response types
interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

interface Product {
  id: string;
  name: string;
  name_en: string;
  price: number;
  currency: string;
  description: string;
  description_en: string;
  image: string;
  in_stock: boolean;
  category: string;
}

interface CatalogResponse {
  products: Product[];
  total: number;
  page: number;
  per_page: number;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

      const response = await fetch(url, {
        headers: { ...defaultHeaders, ...options.headers },
        ...options,
      });

      const data = await response.json();

      return {
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.error || 'Request failed',
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; version: string }>> {
    return this.request('/health');
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  // Catalog
  async getCatalog(): Promise<ApiResponse<CatalogResponse>> {
    return this.request('/catalog');
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
  LoginRequest,
  LoginResponse,
  Product,
  CatalogResponse,
};

// Utility function to check if API is available
export const checkApiConnection = async (): Promise<boolean> => {
  return await apiService.testConnection();
}; 