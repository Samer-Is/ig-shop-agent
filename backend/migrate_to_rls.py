#!/usr/bin/env python3
"""
Database Migration Script: Apply Row-Level Security (RLS) Policies
This script applies enterprise-grade security policies to the existing database
"""

import asyncio
import asyncpg
import logging
from pathlib import Path
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_rls_migration():
    """Apply RLS policies to the database"""
    
    try:
        # Connect to database as admin
        conn = await asyncpg.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            ssl='require'
        )
        
        logger.info("Connected to database as admin")
        
        # Read RLS SQL file
        rls_sql_path = Path(__file__).parent / "database_rls.sql"
        if not rls_sql_path.exists():
            logger.error(f"RLS SQL file not found: {rls_sql_path}")
            return False
        
        with open(rls_sql_path, 'r') as f:
            rls_sql = f.read()
        
        logger.info("Applying RLS policies...")
        
        # Execute RLS SQL in transaction
        async with conn.transaction():
            await conn.execute(rls_sql)
        
        logger.info("✅ RLS policies applied successfully")
        
        # Test RLS functionality
        await test_rls_functionality(conn)
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply RLS migration: {e}")
        return False

async def test_rls_functionality(conn):
    """Test that RLS policies are working correctly"""
    
    logger.info("Testing RLS functionality...")
    
    try:
        # Test 1: Check that RLS is enabled
        rls_enabled = await conn.fetch("""
            SELECT schemaname, tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('users', 'catalog_items', 'orders', 'conversations')
        """)
        
        for table in rls_enabled:
            if table['rowsecurity']:
                logger.info(f"✅ RLS enabled on {table['tablename']}")
            else:
                logger.warning(f"⚠️ RLS not enabled on {table['tablename']}")
        
        # Test 2: Check that policies exist
        policies = await conn.fetch("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname
        """)
        
        logger.info(f"Found {len(policies)} RLS policies:")
        for policy in policies:
            logger.info(f"  - {policy['tablename']}.{policy['policyname']} ({policy['cmd']})")
        
        # Test 3: Check that roles exist
        roles = await conn.fetch("""
            SELECT rolname FROM pg_roles 
            WHERE rolname IN ('app_user', 'admin_user')
        """)
        
        for role in roles:
            logger.info(f"✅ Role exists: {role['rolname']}")
        
        # Test 4: Check that audit functions exist
        functions = await conn.fetch("""
            SELECT proname FROM pg_proc 
            WHERE proname IN ('get_current_user_id', 'audit_trigger_function', 'cleanup_old_data')
        """)
        
        for func in functions:
            logger.info(f"✅ Function exists: {func['proname']}")
        
        logger.info("✅ RLS functionality test completed")
        
    except Exception as e:
        logger.error(f"❌ RLS functionality test failed: {e}")

async def rollback_rls_migration():
    """Rollback RLS policies (for emergency use only)"""
    
    logger.warning("⚠️ Rolling back RLS policies...")
    
    try:
        conn = await asyncpg.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            ssl='require'
        )
        
        # Disable RLS on all tables
        tables = ['users', 'catalog_items', 'orders', 'conversations', 'kb_documents', 'business_rules', 'audit_log']
        
        async with conn.transaction():
            for table in tables:
                await conn.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
                await conn.execute(f"DROP POLICY IF EXISTS {table}_isolation_policy ON {table}")
                await conn.execute(f"DROP POLICY IF EXISTS admin_bypass_policy ON {table}")
                logger.info(f"Disabled RLS on {table}")
        
        logger.info("✅ RLS policies rolled back")
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to rollback RLS: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_rls_migration())
    else:
        success = asyncio.run(apply_rls_migration())
        if not success:
            sys.exit(1) 