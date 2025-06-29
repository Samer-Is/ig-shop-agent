"""
IG-Shop-Agent Multi-Tenant Architecture Test Script
Test tenant isolation, identification, and data separation
"""
import os
import sys
import asyncio
import json
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tenant_middleware import (
    tenant_context,
    tenant_middleware,
    TenantContext,
    HeaderBasedTenantStrategy,
    JWTBasedTenantStrategy,
    PathBasedTenantStrategy,
    SubdomainBasedTenantStrategy,
    tenant_db,
    get_current_tenant_id,
    get_current_tenant_info,
    process_tenant_request,
    require_tenant,
    with_tenant
)
from database import init_database, close_database, db
from instagram_oauth import generate_session_token

async def setup_test_tenants():
    """Set up test tenants for testing"""
    print("🏗️  Setting up test tenants...")
    
    try:
        # Create test tenants
        tenant1_id = await db.create_tenant("@test_store_1", "Test Store 1", "professional")
        tenant2_id = await db.create_tenant("@test_store_2", "Test Store 2", "enterprise")
        
        print(f"✅ Created test tenant 1: {tenant1_id}")
        print(f"✅ Created test tenant 2: {tenant2_id}")
        
        # Create users for tenants
        user1_id = await db.create_user(tenant1_id, "admin@store1.com")
        user2_id = await db.create_user(tenant2_id, "admin@store2.com")
        
        print(f"✅ Created user for tenant 1: {user1_id}")
        print(f"✅ Created user for tenant 2: {user2_id}")
        
        return {
            'tenant1': {'id': tenant1_id, 'handle': '@test_store_1', 'user_id': user1_id},
            'tenant2': {'id': tenant2_id, 'handle': '@test_store_2', 'user_id': user2_id}
        }
        
    except Exception as e:
        print(f"❌ Failed to set up test tenants: {e}")
        return None

async def cleanup_test_tenants(tenants):
    """Clean up test tenants"""
    print("\n🧹 Cleaning up test tenants...")
    
    try:
        if tenants:
            async with db.get_connection() as conn:
                await conn.execute("DELETE FROM tenants WHERE instagram_handle IN ($1, $2)", 
                                 tenants['tenant1']['handle'], tenants['tenant2']['handle'])
            print("✅ Test tenants cleaned up")
    except Exception as e:
        print(f"⚠️  Failed to clean up test tenants: {e}")

def test_tenant_context():
    """Test tenant context management"""
    print("🔧 Testing Tenant Context Management...")
    
    try:
        # Test setting and getting tenant
        test_tenant_id = "test-tenant-123"
        
        # Initially should be None
        if tenant_context.get_tenant_id() is None:
            print("✅ Initial tenant context is None")
        else:
            print("❌ Initial tenant context should be None")
            return False
        
        # Set tenant
        tenant_context.set_tenant(test_tenant_id)
        
        # Check if set correctly
        if tenant_context.get_tenant_id() == test_tenant_id:
            print(f"✅ Tenant context set correctly: {test_tenant_id}")
        else:
            print("❌ Tenant context not set correctly")
            return False
        
        # Clear tenant
        tenant_context.clear_tenant()
        
        # Should be None again
        if tenant_context.get_tenant_id() is None:
            print("✅ Tenant context cleared successfully")
        else:
            print("❌ Tenant context not cleared")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tenant context test failed: {e}")
        return False

def test_tenant_identification_strategies():
    """Test different tenant identification strategies"""
    print("\n🔍 Testing Tenant Identification Strategies...")
    
    try:
        # Test Header-based strategy
        header_strategy = HeaderBasedTenantStrategy()
        
        request_data = {
            'headers': {
                'X-Tenant-ID': 'header-tenant-123',
                'Content-Type': 'application/json'
            }
        }
        
        loop = asyncio.get_event_loop()
        tenant_id = loop.run_until_complete(header_strategy.identify_tenant(request_data))
        
        if tenant_id == 'header-tenant-123':
            print("✅ Header-based tenant identification working")
        else:
            print(f"❌ Header-based identification failed: {tenant_id}")
            return False
        
        # Test JWT-based strategy
        jwt_strategy = JWTBasedTenantStrategy()
        
        # Generate a test JWT token
        user_data = {'id': '123', 'username': 'testuser'}
        jwt_token = generate_session_token(user_data, 'jwt-tenant-456')
        
        request_data = {
            'headers': {
                'Authorization': f'Bearer {jwt_token}'
            }
        }
        
        tenant_id = loop.run_until_complete(jwt_strategy.identify_tenant(request_data))
        
        if tenant_id == 'jwt-tenant-456':
            print("✅ JWT-based tenant identification working")
        else:
            print(f"❌ JWT-based identification failed: {tenant_id}")
            return False
        
        # Test Path-based strategy
        path_strategy = PathBasedTenantStrategy()
        
        request_data = {
            'url': '/api/v1/tenant/path-tenant-789/catalog'
        }
        
        tenant_id = loop.run_until_complete(path_strategy.identify_tenant(request_data))
        
        if tenant_id == 'path-tenant-789':
            print("✅ Path-based tenant identification working")
        else:
            print(f"❌ Path-based identification failed: {tenant_id}")
            return False
        
        # Test Subdomain-based strategy
        subdomain_strategy = SubdomainBasedTenantStrategy()
        
        request_data = {
            'headers': {
                'Host': 'teststore.igshop.com'
            }
        }
        
        tenant_id = loop.run_until_complete(subdomain_strategy.identify_tenant(request_data))
        
        if tenant_id == '@teststore':
            print("✅ Subdomain-based tenant identification working")
        else:
            print(f"❌ Subdomain-based identification failed: {tenant_id}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tenant identification strategies test failed: {e}")
        return False

async def test_tenant_middleware(tenants):
    """Test tenant middleware processing"""
    print("\n🚀 Testing Tenant Middleware...")
    
    try:
        # Test request with valid tenant (JWT)
        user_data = {'id': '123', 'username': 'testuser'}
        jwt_token = generate_session_token(user_data, tenants['tenant1']['id'])
        
        request_data = {
            'headers': {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            },
            'url': '/api/v1/catalog',
            'method': 'GET'
        }
        
        result = await tenant_middleware.process_request(request_data)
        
        if result['success'] and result['tenant_id'] == tenants['tenant1']['id']:
            print(f"✅ Middleware processed valid tenant request: {result['tenant_info']['display_name']}")
        else:
            print(f"❌ Middleware failed to process valid tenant: {result}")
            return False
        
        # Test request with invalid tenant
        request_data = {
            'headers': {
                'X-Tenant-ID': 'invalid-tenant-123'
            }
        }
        
        result = await tenant_middleware.process_request(request_data)
        
        if not result['success'] and 'not found' in result.get('error', ''):
            print("✅ Middleware correctly rejected invalid tenant")
        else:
            print(f"❌ Middleware should reject invalid tenant: {result}")
            return False
        
        # Test request without tenant (should allow for public endpoints)
        request_data = {
            'headers': {
                'Content-Type': 'application/json'
            },
            'url': '/api/v1/public/health'
        }
        
        result = await tenant_middleware.process_request(request_data)
        
        if result['success'] and result['tenant_id'] is None:
            print("✅ Middleware allows requests without tenant context")
        else:
            print(f"❌ Middleware should allow public requests: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tenant middleware test failed: {e}")
        return False

async def test_tenant_data_isolation(tenants):
    """Test that tenant data is properly isolated"""
    print("\n🔒 Testing Tenant Data Isolation...")
    
    try:
        # Set tenant 1 context and create data
        tenant_context.set_tenant(tenants['tenant1']['id'])
        
        item1_data = {
            'sku': 'TEST-001',
            'name': 'Test Product 1',
            'price_jod': 25.99,
            'description': 'Test product for tenant 1'
        }
        
        item1_id = await tenant_db.create_catalog_item(item1_data)
        print(f"✅ Created item for tenant 1: {item1_id}")
        
        # Set tenant 2 context and create data
        tenant_context.set_tenant(tenants['tenant2']['id'])
        
        item2_data = {
            'sku': 'TEST-002',
            'name': 'Test Product 2',
            'price_jod': 35.99,
            'description': 'Test product for tenant 2'
        }
        
        item2_id = await tenant_db.create_catalog_item(item2_data)
        print(f"✅ Created item for tenant 2: {item2_id}")
        
        # Get items for tenant 1 - should only see tenant 1 items
        tenant_context.set_tenant(tenants['tenant1']['id'])
        tenant1_items = await tenant_db.get_catalog_items()
        
        if len(tenant1_items) == 1 and tenant1_items[0]['sku'] == 'TEST-001':
            print("✅ Tenant 1 can only see their own catalog items")
        else:
            print(f"❌ Tenant 1 data isolation failed: {len(tenant1_items)} items found")
            return False
        
        # Get items for tenant 2 - should only see tenant 2 items
        tenant_context.set_tenant(tenants['tenant2']['id'])
        tenant2_items = await tenant_db.get_catalog_items()
        
        if len(tenant2_items) == 1 and tenant2_items[0]['sku'] == 'TEST-002':
            print("✅ Tenant 2 can only see their own catalog items")
        else:
            print(f"❌ Tenant 2 data isolation failed: {len(tenant2_items)} items found")
            return False
        
        # Test order isolation
        tenant_context.set_tenant(tenants['tenant1']['id'])
        
        order1_data = {
            'sku': 'TEST-001',
            'qty': 2,
            'customer': 'John Doe',
            'phone': '+962701234567',
            'total_amount': 51.98
        }
        
        order1_id = await tenant_db.create_order(order1_data)
        print(f"✅ Created order for tenant 1: {order1_id}")
        
        # Check orders for tenant 1
        tenant1_orders = await tenant_db.get_orders()
        
        if len(tenant1_orders) == 1 and tenant1_orders[0]['customer'] == 'John Doe':
            print("✅ Tenant 1 order isolation working")
        else:
            print(f"❌ Tenant 1 order isolation failed: {len(tenant1_orders)} orders found")
            return False
        
        # Check orders for tenant 2 (should be empty)
        tenant_context.set_tenant(tenants['tenant2']['id'])
        tenant2_orders = await tenant_db.get_orders()
        
        if len(tenant2_orders) == 0:
            print("✅ Tenant 2 has no access to tenant 1 orders")
        else:
            print(f"❌ Tenant 2 should not see tenant 1 orders: {len(tenant2_orders)} orders found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tenant data isolation test failed: {e}")
        return False

def test_decorators():
    """Test tenant decorators"""
    print("\n🎭 Testing Tenant Decorators...")
    
    try:
        @require_tenant
        async def tenant_required_function():
            return f"Executed with tenant: {get_current_tenant_id()}"
        
        @with_tenant("decorator-test-tenant")
        async def with_tenant_function():
            return f"Executed with tenant: {get_current_tenant_id()}"
        
        loop = asyncio.get_event_loop()
        
        # Test require_tenant decorator without tenant context
        try:
            result = loop.run_until_complete(tenant_required_function())
            print("❌ @require_tenant should fail without tenant context")
            return False
        except ValueError as e:
            if "Tenant context required" in str(e):
                print("✅ @require_tenant correctly requires tenant context")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        # Test require_tenant decorator with tenant context
        tenant_context.set_tenant("test-tenant-123")
        result = loop.run_until_complete(tenant_required_function())
        
        if "test-tenant-123" in result:
            print("✅ @require_tenant works with tenant context")
        else:
            print(f"❌ @require_tenant failed: {result}")
            return False
        
        # Test with_tenant decorator
        tenant_context.clear_tenant()
        result = loop.run_until_complete(with_tenant_function())
        
        if "decorator-test-tenant" in result:
            print("✅ @with_tenant sets temporary tenant context")
        else:
            print(f"❌ @with_tenant failed: {result}")
            return False
        
        # Verify original context is restored
        if tenant_context.get_tenant_id() is None:
            print("✅ @with_tenant restores original context")
        else:
            print("❌ @with_tenant should restore original context")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("🏢 IG-Shop-Agent Multi-Tenant Architecture Test Suite")
    print("=" * 60)
    
    # Initialize database
    print("🔧 Initializing database...")
    await init_database()
    
    tenants = None
    
    try:
        # Set up test data
        tenants = await setup_test_tenants()
        if not tenants:
            print("❌ Failed to set up test tenants")
            return False
        
        # Run tests
        tests = [
            ("Tenant Context Management", lambda: test_tenant_context()),
            ("Tenant Identification Strategies", lambda: test_tenant_identification_strategies()),
            ("Tenant Middleware", lambda: test_tenant_middleware(tenants)),
            ("Tenant Data Isolation", lambda: test_tenant_data_isolation(tenants)),
            ("Tenant Decorators", lambda: test_decorators())
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            if test_name in ["Tenant Middleware", "Tenant Data Isolation"]:
                # Async tests
                result = await test_func()
            else:
                # Sync tests
                result = test_func()
            
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        
        # Clear tenant context
        tenant_context.clear_tenant()
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL MULTI-TENANT TESTS PASSED!")
            print("✅ Multi-tenant architecture is working correctly")
        else:
            print(f"⚠️  {total - passed} tests failed")
            print("🔧 Some functionality needs attention")
        
        print("=" * 60)
        return passed == total
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if tenants:
            await cleanup_test_tenants(tenants)
        await close_database()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 