"""
IG-Shop-Agent Database Module
PostgreSQL with Row-Level Security and pgvector for multi-tenant SaaS
"""
import os
import asyncpg
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv('DATABASE_URL')
        
    async def initialize(self):
        """Initialize database connection pool and create schema"""
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            # Create schema and enable extensions
            await self.create_schema()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def create_schema(self):
        """Create complete database schema with RLS"""
        schema_sql = """
        -- Enable required extensions
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";
        CREATE EXTENSION IF NOT EXISTS "vector";

        -- Tenants table
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            instagram_handle TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            plan TEXT NOT NULL CHECK (plan IN ('starter', 'professional', 'enterprise')),
            status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'trial')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin' CHECK (role IN ('admin', 'manager', 'agent')),
            last_login TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(tenant_id, email)
        );

        -- Meta tokens (encrypted)
        CREATE TABLE IF NOT EXISTS meta_tokens (
            tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
            access_token TEXT NOT NULL, -- encrypted
            refresh_token TEXT,
            expires_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Catalog items
        CREATE TABLE IF NOT EXISTS catalog_items (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            sku TEXT NOT NULL,
            name TEXT NOT NULL,
            price_jod DECIMAL(10,2) NOT NULL,
            media_url TEXT,
            description TEXT,
            category TEXT,
            stock_quantity INTEGER DEFAULT 0,
            extras JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(tenant_id, sku)
        );

        -- Orders
        CREATE TABLE IF NOT EXISTS orders (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            sku TEXT NOT NULL,
            qty INTEGER NOT NULL,
            customer TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' 
                CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
            total_amount DECIMAL(10,2) NOT NULL,
            delivery_address TEXT,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Knowledge base documents
        CREATE TABLE IF NOT EXISTS kb_documents (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            file_uri TEXT NOT NULL,
            title TEXT NOT NULL,
            vector_id TEXT,
            content_preview TEXT,
            file_type TEXT,
            file_size BIGINT,
            embedding VECTOR(1536), -- OpenAI embedding dimensions
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Business profiles (YAML stored as JSONB)
        CREATE TABLE IF NOT EXISTS profiles (
            tenant_id UUID PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
            yaml_profile JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Conversations
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            ts TIMESTAMPTZ DEFAULT NOW(),
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            message_type TEXT DEFAULT 'incoming' CHECK (message_type IN ('incoming', 'outgoing')),
            ai_generated BOOLEAN DEFAULT false,
            context JSONB DEFAULT '{}'
        );

        -- Usage statistics
        CREATE TABLE IF NOT EXISTS usage_stats (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            openai_cost_usd DECIMAL(10,4) DEFAULT 0,
            meta_messages INTEGER DEFAULT 0,
            total_conversations INTEGER DEFAULT 0,
            orders_created INTEGER DEFAULT 0,
            customer_satisfaction DECIMAL(3,2),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(tenant_id, date)
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_catalog_items_tenant_id ON catalog_items(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_orders_tenant_id ON orders(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_conversations_tenant_id ON conversations(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_ts ON conversations(ts);
        CREATE INDEX IF NOT EXISTS idx_kb_documents_tenant_id ON kb_documents(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_usage_stats_tenant_id_date ON usage_stats(tenant_id, date);

        -- Enable Row-Level Security
        ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE meta_tokens ENABLE ROW LEVEL SECURITY;
        ALTER TABLE catalog_items ENABLE ROW LEVEL SECURITY;
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        ALTER TABLE kb_documents ENABLE ROW LEVEL SECURITY;
        ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
        ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE usage_stats ENABLE ROW LEVEL SECURITY;

        -- Create RLS policies (tenant-based isolation)
        -- Admin role bypasses RLS, regular users see only their tenant data
        
        -- Tenants policies
        DROP POLICY IF EXISTS tenant_isolation_policy ON tenants;
        CREATE POLICY tenant_isolation_policy ON tenants
            FOR ALL TO PUBLIC
            USING (id = current_setting('app.current_tenant_id')::uuid);

        -- Users policies  
        DROP POLICY IF EXISTS users_tenant_policy ON users;
        CREATE POLICY users_tenant_policy ON users
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Catalog items policies
        DROP POLICY IF EXISTS catalog_tenant_policy ON catalog_items;
        CREATE POLICY catalog_tenant_policy ON catalog_items
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Orders policies
        DROP POLICY IF EXISTS orders_tenant_policy ON orders;
        CREATE POLICY orders_tenant_policy ON orders
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- KB documents policies
        DROP POLICY IF EXISTS kb_tenant_policy ON kb_documents;
        CREATE POLICY kb_tenant_policy ON kb_documents
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Profiles policies
        DROP POLICY IF EXISTS profiles_tenant_policy ON profiles;
        CREATE POLICY profiles_tenant_policy ON profiles
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Conversations policies
        DROP POLICY IF EXISTS conversations_tenant_policy ON conversations;
        CREATE POLICY conversations_tenant_policy ON conversations
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Usage stats policies
        DROP POLICY IF EXISTS usage_tenant_policy ON usage_stats;
        CREATE POLICY usage_tenant_policy ON usage_stats
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

        -- Meta tokens policies
        DROP POLICY IF EXISTS meta_tokens_tenant_policy ON meta_tokens;
        CREATE POLICY meta_tokens_tenant_policy ON meta_tokens
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(schema_sql)
            logger.info("Database schema created successfully")

    @asynccontextmanager
    async def get_connection(self, tenant_id: Optional[str] = None):
        """Get database connection with optional tenant context"""
        if not self.pool:
            raise RuntimeError("Database not initialized")
            
        async with self.pool.acquire() as conn:
            if tenant_id:
                await conn.execute("SET app.current_tenant_id = $1", tenant_id)
            try:
                yield conn
            finally:
                if tenant_id:
                    await conn.execute("RESET app.current_tenant_id")

    async def create_tenant(self, instagram_handle: str, display_name: str, plan: str = 'professional') -> str:
        """Create new tenant"""
        async with self.get_connection() as conn:
            tenant_id = await conn.fetchval("""
                INSERT INTO tenants (instagram_handle, display_name, plan)
                VALUES ($1, $2, $3)
                RETURNING id
            """, instagram_handle, display_name, plan)
            
            logger.info(f"Created tenant {tenant_id} for {instagram_handle}")
            return str(tenant_id)

    async def get_tenant_by_handle(self, instagram_handle: str) -> Optional[Dict[str, Any]]:
        """Get tenant by Instagram handle"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow("""
                SELECT id, instagram_handle, display_name, plan, status, created_at
                FROM tenants 
                WHERE instagram_handle = $1
            """, instagram_handle)
            
            if row:
                return dict(row)
            return None

    async def create_user(self, tenant_id: str, email: str, role: str = 'admin') -> str:
        """Create new user for tenant"""
        async with self.get_connection(tenant_id) as conn:
            user_id = await conn.fetchval("""
                INSERT INTO users (tenant_id, email, role)
                VALUES ($1, $2, $3)
                RETURNING id
            """, tenant_id, email, role)
            
            return str(user_id)

    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")

# Global database instance
db = DatabaseManager()

async def init_database():
    """Initialize database - call this on startup"""
    await db.initialize()

async def close_database():
    """Close database - call this on shutdown"""
    await db.close() 