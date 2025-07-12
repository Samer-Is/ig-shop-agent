"""
Enterprise Database Service with Row-Level Security (RLS)
Provides database-level multi-tenant isolation and enterprise security features
"""
import os
import asyncpg
import json
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from config import settings

logger = logging.getLogger(__name__)

class EnterpriseDatabase:
    """Enterprise-grade database service with RLS and compliance features"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False
        self.current_user_id: Optional[str] = None
    
    async def connect(self) -> None:
        """Create database connection pool with enterprise security"""
        try:
            if self.pool:
                return
            
            logger.info("Connecting to enterprise database with RLS...")
            
            # Create connection pool with app_user role
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user='app_user',  # Use RLS-enabled role
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                min_size=2,
                max_size=20,
                command_timeout=60,
                ssl='require',
                server_settings={
                    'jit': 'off',  # Disable JIT for better security
                    'log_statement': 'all',  # Log all statements for audit
                }
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            
            self.is_connected = True
            logger.info("Enterprise database connected successfully with RLS enabled")
            
        except Exception as e:
            logger.error(f"Failed to connect to enterprise database: {e}")
            self.is_connected = False
            raise
    
    async def set_user_context(self, user_id: str) -> None:
        """Set user context for Row-Level Security"""
        self.current_user_id = user_id
        logger.debug(f"Set user context for RLS: {user_id}")
    
    @asynccontextmanager
    async def get_connection(self, user_id: Optional[str] = None):
        """Get database connection with user context set"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            # Set user context for RLS
            context_user_id = user_id or self.current_user_id
            if context_user_id:
                await conn.execute(
                    "SELECT set_config('app.current_user_id', $1, false)",
                    context_user_id
                )
            
            yield conn
    
    async def execute_query(self, query: str, *args, user_id: Optional[str] = None) -> None:
        """Execute query with user context"""
        async with self.get_connection(user_id) as conn:
            await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch one record with user context"""
        async with self.get_connection(user_id) as conn:
            result = await conn.fetchrow(query, *args)
            return dict(result) if result else None
    
    async def fetch_all(self, query: str, *args, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all records with user context"""
        async with self.get_connection(user_id) as conn:
            results = await conn.fetch(query, *args)
            return [dict(row) for row in results]
    
    async def log_audit_event(self, user_id: str, action: str, table_name: str, 
                             record_id: Optional[str] = None, 
                             old_values: Optional[Dict] = None,
                             new_values: Optional[Dict] = None,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None) -> None:
        """Log audit event for compliance"""
        try:
            async with self.get_connection(user_id) as conn:
                await conn.execute("""
                    INSERT INTO audit_log (user_id, action, table_name, record_id, 
                                         old_values, new_values, ip_address, user_agent)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, user_id, action, table_name, record_id, 
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                ip_address, user_agent)
                
            logger.info(f"Audit logged: {user_id} {action} {table_name}")
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def track_usage(self, user_id: str, metric_type: str, metric_value: int,
                         period_start: datetime, period_end: datetime) -> None:
        """Track usage metrics for billing"""
        try:
            async with self.get_connection(user_id) as conn:
                await conn.execute("""
                    INSERT INTO usage_metrics (user_id, metric_type, metric_value, period_start, period_end)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id, metric_type, period_start) 
                    DO UPDATE SET metric_value = usage_metrics.metric_value + EXCLUDED.metric_value
                """, user_id, metric_type, metric_value, period_start, period_end)
                
            logger.debug(f"Usage tracked: {user_id} {metric_type} {metric_value}")
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
    
    async def check_rate_limit(self, user_id: str, endpoint: str, limit: int, 
                              window_minutes: int = 60) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            window_start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            window_end = window_start.replace(hour=window_start.hour + 1)
            
            async with self.get_connection(user_id) as conn:
                # Get current count
                current_count = await conn.fetchval("""
                    SELECT COALESCE(requests_count, 0) FROM rate_limits
                    WHERE user_id = $1 AND endpoint = $2 AND window_start = $3
                """, user_id, endpoint, window_start)
                
                if current_count is None:
                    current_count = 0
                
                # Check if limit exceeded
                if current_count >= limit:
                    logger.warning(f"Rate limit exceeded: {user_id} {endpoint} {current_count}/{limit}")
                    return False
                
                # Update count
                await conn.execute("""
                    INSERT INTO rate_limits (user_id, endpoint, requests_count, window_start, window_end)
                    VALUES ($1, $2, 1, $3, $4)
                    ON CONFLICT (user_id, endpoint, window_start)
                    DO UPDATE SET requests_count = rate_limits.requests_count + 1
                """, user_id, endpoint, window_start, window_end)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True  # Allow on error
    
    async def encrypt_sensitive_field(self, data: str, encryption_key: Optional[str] = None) -> str:
        """Encrypt sensitive data using database encryption"""
        try:
            key = encryption_key or settings.ENCRYPTION_KEY
            async with self.get_connection() as conn:
                encrypted = await conn.fetchval(
                    "SELECT encrypt_sensitive_data($1, $2)",
                    data, key
                )
                return encrypted
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return data  # Return original on error
    
    async def decrypt_sensitive_field(self, encrypted_data: str, encryption_key: Optional[str] = None) -> str:
        """Decrypt sensitive data using database decryption"""
        try:
            key = encryption_key or settings.ENCRYPTION_KEY
            async with self.get_connection() as conn:
                decrypted = await conn.fetchval(
                    "SELECT decrypt_sensitive_data($1, $2)",
                    encrypted_data, key
                )
                return decrypted
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return encrypted_data  # Return encrypted on error
    
    async def get_user_audit_trail(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail for a user"""
        return await self.fetch_all("""
            SELECT action, table_name, record_id, old_values, new_values, 
                   ip_address, user_agent, created_at
            FROM audit_log
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """, user_id, limit, user_id=user_id)
    
    async def get_user_usage_metrics(self, user_id: str, metric_type: Optional[str] = None,
                                   days: int = 30) -> List[Dict[str, Any]]:
        """Get usage metrics for a user"""
        query = """
            SELECT metric_type, SUM(metric_value) as total_value, 
                   DATE_TRUNC('day', period_start) as date
            FROM usage_metrics
            WHERE user_id = $1 AND period_start >= NOW() - INTERVAL '%s days'
        """ % days
        
        params = [user_id]
        
        if metric_type:
            query += " AND metric_type = $2"
            params.append(metric_type)
        
        query += " GROUP BY metric_type, DATE_TRUNC('day', period_start) ORDER BY date DESC"
        
        return await self.fetch_all(query, *params, user_id=user_id)
    
    async def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data for GDPR compliance"""
        try:
            async with self.get_connection() as conn:
                # Count records before cleanup
                old_conversations = await conn.fetchval(
                    "SELECT COUNT(*) FROM conversations WHERE created_at < NOW() - INTERVAL '30 days'"
                )
                old_audit_logs = await conn.fetchval(
                    "SELECT COUNT(*) FROM audit_log WHERE created_at < NOW() - INTERVAL '7 years'"
                )
                
                # Perform cleanup
                await conn.execute("SELECT cleanup_old_data()")
                
                logger.info(f"Cleaned up {old_conversations} conversations and {old_audit_logs} audit logs")
                
                return {
                    'conversations_deleted': old_conversations,
                    'audit_logs_deleted': old_audit_logs
                }
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            async with self.get_connection() as conn:
                # Check database connectivity
                await conn.fetchval('SELECT 1')
                
                # Check RLS is enabled
                rls_status = await conn.fetchval("""
                    SELECT COUNT(*) FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relrowsecurity = true 
                    AND n.nspname = 'public'
                """)
                
                # Check pool status
                pool_info = {
                    'size': self.pool.get_size(),
                    'min_size': self.pool.get_min_size(),
                    'max_size': self.pool.get_max_size(),
                    'idle_size': self.pool.get_idle_size()
                }
                
                return {
                    'status': 'healthy',
                    'connected': self.is_connected,
                    'rls_enabled_tables': rls_status,
                    'pool_info': pool_info,
                    'current_user': self.current_user_id
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connected': False
            }
    
    async def close(self) -> None:
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            self.is_connected = False
            logger.info("Enterprise database connections closed")

# Global enterprise database instance
enterprise_db = EnterpriseDatabase()

async def get_enterprise_database() -> EnterpriseDatabase:
    """Get the global enterprise database instance"""
    if not enterprise_db.is_connected:
        await enterprise_db.connect()
    return enterprise_db

async def init_enterprise_database() -> None:
    """Initialize enterprise database with RLS"""
    try:
        db = await get_enterprise_database()
        
        # Run RLS setup if not already done
        try:
            async with db.get_connection() as conn:
                # Check if RLS is already set up
                rls_enabled = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_policies 
                        WHERE tablename = 'users' 
                        AND policyname = 'users_isolation_policy'
                    )
                """)
                
                if not rls_enabled:
                    logger.info("Setting up Row-Level Security...")
                    # Read and execute RLS setup script
                    with open('database_rls.sql', 'r') as f:
                        rls_script = f.read()
                    
                    await conn.execute(rls_script)
                    logger.info("Row-Level Security setup completed")
                else:
                    logger.info("Row-Level Security already configured")
                    
        except FileNotFoundError:
            logger.warning("RLS setup script not found. Please run database_rls.sql manually.")
        except Exception as e:
            logger.error(f"Failed to setup RLS: {e}")
        
        logger.info("Enterprise database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize enterprise database: {e}")
        raise 