// Database Schema Types based on requirements
export interface Tenant {
  id: string;
  instagram_handle: string;
  display_name: string;
  plan: 'starter' | 'professional' | 'enterprise';
  created_at: string;
  status: 'active' | 'suspended' | 'trial';
}

export interface User {
  id: number;
  instagram_handle: string;
  instagram_connected: boolean;
  tenant_id?: string;
  email: string;
  business_name?: string;
  username?: string;     // Required by Header component
  name?: string;         // Required by Header component
  role?: 'admin' | 'manager' | 'agent';
  last_login?: string;
  created_at?: string;
}

export interface MetaToken {
  tenant_id: string;
  access_token: string; // encrypted
  expires_at: string;
  created_at: string;
}

export interface CatalogItem {
  id: number;
  sku: string;
  name: string;
  description?: string;
  price_jod: number;
  category?: string;
  media_url?: string;
  stock_quantity?: number;
  is_active: boolean;
  created_at: string;
}

export interface Order {
  id: number;
  sku: string;
  qty: number;
  customer: string;
  phone: string;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  delivery_address?: string;
  notes?: string;
  created_at: string;
}

export interface KBDocument {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

export interface BusinessProfile {
  tenant_id: string;
  yaml_profile: {
    business_name: string;
    description: string;
    contact_info: {
      email: string;
      phone: string;
      address: string;
    };
    operating_hours: {
      sunday: string;
      monday: string;
      tuesday: string;
      wednesday: string;
      thursday: string;
      friday: string;
      saturday: string;
    };
    policies: {
      shipping: string;
      returns: string;
      payment: string;
    };
    ai_personality: {
      tone: string;
      language: string;
      greeting: string;
      response_style?: string;
    };
  };
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number;
  customer: string;
  message: string;
  is_ai_response: boolean;
  created_at: string;
}

export interface UsageStats {
  id: string;
  tenant_id: string;
  date: string;
  openai_cost_usd: number;
  meta_messages: number;
  total_conversations: number;
  orders_created: number;
  customer_satisfaction?: number;
}

export interface AIFunction {
  name: string;
  description: string;
  parameters: Record<string, any>;
  enabled: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface DashboardStats {
  total_conversations: number;
  active_orders: number;
  revenue_this_month: number;
  ai_cost_this_month: number;
  customer_satisfaction: number;
  response_time_avg: number;
  conversion_rate: number;
  top_products: CatalogItem[];
  recent_orders: Order[];
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
}
