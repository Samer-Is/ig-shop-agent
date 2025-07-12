"""
IG-Shop-Agent Database Module
PostgreSQL with Row-Level Security and pgvector for multi-tenant SaaS
"""
import os
import asyncpg
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timezone
import logging
from contextlib import asynccontextmanager
from config import settings

logger = logging.getLogger(__name__)

# Global database service instance
db_service = None

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
                ssl='require'  # Azure PostgreSQL requires SSL
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
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            try:
                yield conn
            except Exception as e:
                logger.error(f"Database error: {e}")
                raise
    
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
                instagram_page_id TEXT,
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
                product_link TEXT DEFAULT '',
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
            
            -- Business rules and configuration table
            CREATE TABLE IF NOT EXISTS business_rules (
                id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                business_name TEXT,
                business_type TEXT,
                working_hours TEXT,
                delivery_info TEXT,
                payment_methods TEXT,
                return_policy TEXT,
                terms_conditions TEXT,
                contact_info TEXT,
                custom_prompt TEXT,
                ai_instructions TEXT,
                language_preference TEXT DEFAULT 'en,ar',
                response_tone TEXT DEFAULT 'professional',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(user_id)
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
            
            # Add migration for instagram_page_id column if it doesn't exist
            try:
                async with self.get_connection() as conn:
                    await conn.execute("""
                        ALTER TABLE users 
                        ADD COLUMN IF NOT EXISTS instagram_page_id TEXT;
                    """)
                logger.info("Migration: Added instagram_page_id column")
            except Exception as e:
                logger.warning(f"Migration warning (likely already exists): {e}")
            
            # Add sentiment and intent tracking columns for Phase 4 analytics
            await self.execute_query("""
                ALTER TABLE conversations 
                ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20),
                ADD COLUMN IF NOT EXISTS intent VARCHAR(50),
                ADD COLUMN IF NOT EXISTS products_mentioned TEXT[]
            """)
            logger.info("Migration: Added sentiment, intent, and products_mentioned columns")
            
            # Create indexes for better query performance
            await self.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_conversations_sentiment ON conversations(sentiment);
                CREATE INDEX IF NOT EXISTS idx_conversations_intent ON conversations(intent);
                CREATE INDEX IF NOT EXISTS idx_conversations_user_customer ON conversations(user_id, customer);
            """)
            logger.info("Migration: Added indexes for conversation analytics")
            
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            return False
    
    async def store_instagram_tokens(self, instagram_account_id: str, access_token: str, account_data: Dict[str, Any]) -> None:
        """Store Instagram tokens and account info in database"""
        try:
            async with self.get_connection() as conn:
                # Start transaction
                async with conn.transaction():
                    # Check if user exists
                    existing_user = await conn.fetchrow(
                        "SELECT id FROM users WHERE instagram_user_id = $1",
                        instagram_account_id
                    )
                    
                    if existing_user:
                        # Update existing user
                        await conn.execute(
                            """
                            UPDATE users 
                            SET instagram_access_token = $1,
                                instagram_connected = TRUE,
                                updated_at = NOW()
                            WHERE instagram_user_id = $2
                            """,
                            access_token,
                            instagram_account_id
                        )
                    else:
                        # Create new user
                        await conn.execute(
                            """
                            INSERT INTO users (
                                instagram_handle,
                                instagram_user_id,
                                instagram_access_token,
                                instagram_connected
                            ) VALUES ($1, $2, $3, TRUE)
                            """,
                            account_data['username'],
                            instagram_account_id,
                            access_token
                        )
                        
                    logger.info(f"Successfully stored Instagram tokens for account {instagram_account_id}")
                    
        except Exception as e:
            logger.error(f"Failed to store Instagram tokens: {e}")
            raise

async def get_database() -> DatabaseService:
    """Get the global database service instance"""
    global db_service
    if db_service is None:
        db_service = DatabaseService()
        await db_service.connect()
    return db_service

async def init_database() -> None:
    """Initialize the database connection and schema"""
    try:
        logger.info("Initializing database...")
        db = await get_database()
        
        # Initialize schema
        await db.initialize_schema()
        
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_database() -> None:
    """Close the database connection"""
    global db_service
    if db_service:
        await db_service.disconnect()
        db_service = None

# Dependency for FastAPI
async def get_db() -> DatabaseService:
    """FastAPI dependency to get database service"""
    return await get_database()

# Export for convenience
__all__ = ["db_service", "get_db_connection", "database_lifespan", "DatabaseService"] 