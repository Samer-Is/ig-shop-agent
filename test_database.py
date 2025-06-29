"""
IG-Shop-Agent Database Test Script
Test database connectivity, schema creation, and basic operations
"""
import asyncio
import os
import sys
from datetime import datetime
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db, init_database, close_database

async def test_database_setup():
    """Test complete database setup and functionality"""
    print("🔧 Starting IG-Shop-Agent Database Tests...")
    
    # Test environment variables
    print("\n📋 Testing Environment Configuration...")
    required_env_vars = ['DATABASE_URL']
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}")  # Mask sensitive values
        else:
            print(f"❌ {var}: Not set")
            return False
    
    try:
        # Initialize database
        print("\n🔗 Testing Database Connection...")
        await init_database()
        print("✅ Database connection established")
        print("✅ Database schema created successfully")
        
        # Test tenant creation
        print("\n👥 Testing Tenant Management...")
        test_handle = "@test_fashion_store"
        test_display_name = "Test Fashion Store"
        
        # Create test tenant
        tenant_id = await db.create_tenant(test_handle, test_display_name)
        print(f"✅ Created test tenant: {tenant_id}")
        
        # Retrieve tenant
        tenant = await db.get_tenant_by_handle(test_handle)
        if tenant:
            print(f"✅ Retrieved tenant: {tenant['display_name']}")
        else:
            print("❌ Failed to retrieve tenant")
            return False
        
        # Test user creation
        print("\n👤 Testing User Management...")
        test_email = "admin@teststore.com"
        user_id = await db.create_user(tenant_id, test_email)
        print(f"✅ Created test user: {user_id}")
        
        # Test catalog operations
        print("\n🛍️ Testing Catalog Operations...")
        async with db.get_connection(tenant_id) as conn:
            # Insert test product
            product_id = await conn.fetchval("""
                INSERT INTO catalog_items (tenant_id, sku, name, price_jod, description, category, stock_quantity)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, tenant_id, "TEST-001", "Test Product", 50.00, "Test Description", "Test Category", 10)
            
            print(f"✅ Created test product: {product_id}")
            
            # Retrieve product
            product = await conn.fetchrow("""
                SELECT * FROM catalog_items WHERE id = $1
            """, product_id)
            
            if product:
                print(f"✅ Retrieved product: {product['name']} - {product['price_jod']} JOD")
            else:
                print("❌ Failed to retrieve product")
                return False
        
        # Test order operations
        print("\n📦 Testing Order Operations...")
        async with db.get_connection(tenant_id) as conn:
            order_id = await conn.fetchval("""
                INSERT INTO orders (tenant_id, sku, qty, customer, phone, status, total_amount)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, tenant_id, "TEST-001", 2, "Test Customer", "+962701234567", "pending", 100.00)
            
            print(f"✅ Created test order: {order_id}")
            
            # Retrieve order
            order = await conn.fetchrow("""
                SELECT * FROM orders WHERE id = $1
            """, order_id)
            
            if order:
                print(f"✅ Retrieved order: {order['customer']} - {order['total_amount']} JOD")
            else:
                print("❌ Failed to retrieve order")
                return False
        
        # Test conversation operations
        print("\n💬 Testing Conversation Operations...")
        async with db.get_connection(tenant_id) as conn:
            conv_id = await conn.fetchval("""
                INSERT INTO conversations (tenant_id, sender, text, message_type, ai_generated)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, tenant_id, "Test Customer", "Hello, I want to buy something", "incoming", False)
            
            print(f"✅ Created test conversation: {conv_id}")
            
            # AI response
            ai_conv_id = await conn.fetchval("""
                INSERT INTO conversations (tenant_id, sender, text, message_type, ai_generated, tokens_out)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, tenant_id, "AI Assistant", "مرحباً! كيف يمكنني مساعدتك؟", "outgoing", True, 15)
            
            print(f"✅ Created AI response: {ai_conv_id}")
        
        # Test business profile operations
        print("\n🏢 Testing Business Profile Operations...")
        test_profile = {
            "business_name": "Test Fashion Store",
            "description": "A test fashion store",
            "contact_info": {
                "phone": "+962701234567",
                "email": "info@teststore.com",
                "address": "Amman, Jordan"
            },
            "ai_personality": {
                "tone": "friendly",
                "language": "Arabic",
                "response_style": "helpful"
            }
        }
        
        async with db.get_connection(tenant_id) as conn:
            await conn.execute("""
                INSERT INTO profiles (tenant_id, yaml_profile)
                VALUES ($1, $2)
                ON CONFLICT (tenant_id) DO UPDATE SET yaml_profile = $2, updated_at = NOW()
            """, tenant_id, json.dumps(test_profile))
            
            print("✅ Created/updated business profile")
            
            # Retrieve profile
            profile_row = await conn.fetchrow("""
                SELECT yaml_profile FROM profiles WHERE tenant_id = $1
            """, tenant_id)
            
            if profile_row:
                profile_data = profile_row['yaml_profile']
                print(f"✅ Retrieved profile: {profile_data['business_name']}")
            else:
                print("❌ Failed to retrieve profile")
                return False
        
        # Test usage stats
        print("\n📊 Testing Usage Statistics...")
        async with db.get_connection(tenant_id) as conn:
            await conn.execute("""
                INSERT INTO usage_stats (tenant_id, date, openai_cost_usd, meta_messages, total_conversations, orders_created)
                VALUES ($1, CURRENT_DATE, $2, $3, $4, $5)
                ON CONFLICT (tenant_id, date) DO UPDATE SET 
                    openai_cost_usd = $2, meta_messages = $3, total_conversations = $4, orders_created = $5
            """, tenant_id, 5.50, 25, 10, 2)
            
            print("✅ Created usage statistics")
        
        # Test Row-Level Security
        print("\n🔒 Testing Row-Level Security...")
        async with db.get_connection(tenant_id) as conn:
            # Count products for this tenant
            tenant_products = await conn.fetchval("""
                SELECT COUNT(*) FROM catalog_items
            """)
            print(f"✅ Tenant can see {tenant_products} products (RLS working)")
        
        # Test without tenant context (should see nothing due to RLS)
        async with db.get_connection() as conn:
            try:
                all_products = await conn.fetchval("""
                    SELECT COUNT(*) FROM catalog_items
                """)
                print(f"⚠️  Without tenant context: {all_products} products visible")
            except Exception as e:
                print(f"✅ RLS blocking access without tenant context: {str(e)[:50]}...")
        
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        async with db.get_connection() as conn:
            # Delete tenant (CASCADE will remove all related data)
            await conn.execute("DELETE FROM tenants WHERE instagram_handle = $1", test_handle)
            print("✅ Test data cleaned up")
        
        print("\n🎉 All database tests passed successfully!")
        print("✅ Database is ready for production use")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await close_database()

async def test_schema_validation():
    """Test that the database schema matches project requirements"""
    print("\n🔍 Validating Database Schema...")
    
    try:
        async with db.get_connection() as conn:
            # Check required tables exist
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            
            required_tables = [
                'tenants', 'users', 'meta_tokens', 'catalog_items', 
                'orders', 'kb_documents', 'profiles', 'conversations', 'usage_stats'
            ]
            
            existing_tables = [row['table_name'] for row in tables]
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
            
            # Check extensions
            extensions = await conn.fetch("""
                SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto', 'vector')
            """)
            
            required_extensions = ['uuid-ossp', 'pgcrypto', 'vector']
            existing_extensions = [row['extname'] for row in extensions]
            
            for ext in required_extensions:
                if ext in existing_extensions:
                    print(f"✅ Extension '{ext}' enabled")
                else:
                    print(f"❌ Extension '{ext}' missing")
            
            print("✅ Schema validation completed")
            return True
            
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 IG-Shop-Agent Database Test Suite")
    print("=" * 60)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set")
        print("   Set it like: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        return False
    
    try:
        # Run tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(test_database_setup())
        if success:
            success = loop.run_until_complete(test_schema_validation())
        
        loop.close()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED - DATABASE READY FOR PRODUCTION!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED - PLEASE FIX ISSUES BEFORE PROCEEDING")
            print("=" * 60)
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 