import axios from 'axios';

// ULTIMATE EMERGENCY FIX: Force complete cache invalidation - 2024-12-19 17:15
const API_BASE_URL = 'https://igshop-api.azurewebsites.net';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

export class ApiService {
  async getInstagramAuthUrl() {
    try {
      const response = await api.get('/auth/instagram/login');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  async handleInstagramCallback(code: string, state: string) {
    try {
      const response = await api.post('/auth/instagram/callback', { code, state });
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  async healthCheck() {
    try {
      const response = await api.get('/health');
      return { data: response.data, status: response.status };
    } catch (error: any) {
      return { error: error.message, status: error.response?.status || 500 };
    }
  }

  async getCatalog() {
    try {
      const response = await api.get('/catalog');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async getOrders() {
    try {
      const response = await api.get('/orders');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async getDashboardAnalytics() {
    try {
      const response = await api.get('/backend-api/analytics');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async getConversations() {
    try {
      const response = await api.get('/conversations');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async getKnowledgeBase() {
    try {
      const response = await api.get('/kb');
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async testAIResponse(message: string, businessRules?: any, products?: any[], knowledgeBase?: any[]) {
    try {
      const response = await api.post('/backend-api/ai/test', {
        message,
        business_rules: businessRules || {},
        products: products || [],
        knowledge_base: knowledgeBase || []
      });
      return { data: response.data };
    } catch (error: any) {
      return { error: error.message };
    }
  }

  async testConnection() {
    try {
      const response = await this.healthCheck();
      return response.status === 200;
    } catch {
      return false;
    }
  }

  setAuthToken(token: string) {
    localStorage.setItem('auth_token', token);
  }

  clearAuthToken() {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  }
}

export const apiService = new ApiService();

export const checkApiConnection = async () => {
  try {
    return await apiService.testConnection();
  } catch {
    return false;
  }
};