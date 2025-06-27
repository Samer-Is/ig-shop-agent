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
  id: string;
  tenant_id: string;
  email: string;
  role: 'admin' | 'manager' | 'agent';
  last_login: string;
  created_at: string;
}

export interface MetaToken {
  tenant_id: string;
  access_token: string; // encrypted
  expires_at: string;
  created_at: string;
}

export interface CatalogItem {
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

export interface Order {
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

export interface KBDocument {
  id: string;
  tenant_id: string;
  file_uri: string;
  title: string;
  vector_id: string;
  content_preview?: string;
  file_type: string;
  file_size: number;
  created_at: string;
}

export interface BusinessProfile {
  tenant_id: string;
  yaml_profile: {
    business_name: string;
    description: string;
    contact_info: {
      phone: string;
      email: string;
      address: string;
    };
    operating_hours: {
      [key: string]: string;
    };
    policies: {
      shipping: string;
      returns: string;
      payment: string;
    };
    ai_personality: {
      tone: string;
      language: string;
      response_style: string;
    };
  };
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  tenant_id: string;
  sender: string;
  text: string;
  ts: string;
  tokens_in: number;
  tokens_out: number;
  message_type: 'incoming' | 'outgoing';
  ai_generated: boolean;
  context?: Record<string, any>;
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
