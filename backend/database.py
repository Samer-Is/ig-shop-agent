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
from config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for managing PostgreSQL connections"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False
    
    async def connect(self) -> None:
        """Create database connection pool"""
        try:
            if self.pool:
                return
            
            logger.info("Connecting to database...")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                min_size=1,
                max_size=10,
                command_timeout=60,
                ssl='require' if settings.is_production else 'prefer'
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            
            self.is_connected = True
            logger.info("Database connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Close database connection pool"""
        try:
            if self.pool:
                await self.pool.close()
                self.pool = None
                self.is_connected = False
                logger.info("Database disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            await self.connect()
        return self.pool.acquire()
    
    async def execute_query(self, query: str, *args) -> str:
        """Execute a query and return the result"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch one row from the database"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows from the database"""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetch_val(self, query: str, *args) -> Any:
        """Fetch a single value from the database"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.is_connected:
                return {
                    "status": "disconnected",
                    "error": "Database not connected"
                }
            
            # Test basic query
            result = await self.fetch_val("SELECT 1")
            if result == 1:
                # Get some basic stats
                table_count = await self.fetch_val(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                )
                
                return {
                    "status": "healthy",
                    "connected": True,
                    "tables": table_count,
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "pool_max_size": self.pool.get_max_size() if self.pool else 0
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database query failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def initialize_schema(self) -> bool:
        """Initialize database schema with required tables"""
        try:
            logger.info("Initializing database schema...")
            
            # Create tables if they don't exist
            schema_sql = """
            -- Users table (simplified for Instagram OAuth)
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                instagram_handle TEXT UNIQUE NOT NULL,
                instagram_user_id TEXT UNIQUE,
                instagram_access_token TEXT,
                instagram_connected BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Catalog items table
            CREATE TABLE IF NOT EXISTS catalog_items (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                sku TEXT NOT NULL,
                name TEXT NOT NULL,
                price_jod DECIMAL(10,2) NOT NULL,
                media_url TEXT NOT NULL DEFAULT '',
                extras JSONB DEFAULT '{}',
                description TEXT,
                category TEXT,
                stock_quantity INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id, sku)
            );
            
            -- Orders table
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                sku TEXT NOT NULL,
                qty INTEGER NOT NULL,
                customer TEXT NOT NULL,
                phone TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
                total_amount DECIMAL(10,2) NOT NULL,
                delivery_address TEXT,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Knowledge base documents table
            CREATE TABLE IF NOT EXISTS kb_documents (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                vector_id TEXT UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Conversations table
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                customer TEXT NOT NULL,
                message TEXT NOT NULL,
                is_ai_response BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            async with self.get_connection() as conn:
                await conn.execute(schema_sql)
            
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            return False

# Database service singleton
db_service = DatabaseService()

def get_db_connection():
    """Get database connection for synchronous code"""
    import psycopg2
    return psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_NAME
    )

@asynccontextmanager
async def database_lifespan():
    """Database connection lifecycle manager"""
    try:
        await db_service.connect()
        yield
    finally:
        await db_service.disconnect()

# Export for convenience
__all__ = ["db_service", "get_db_connection", "database_lifespan", "DatabaseService"] 