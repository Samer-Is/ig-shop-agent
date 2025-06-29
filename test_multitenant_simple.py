"""
IG-Shop-Agent Multi-Tenant Architecture Simple Test
Test tenant logic without database dependency
"""
import os
import sys
import asyncio
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the database module to avoid connection issues
class MockDB:
    async def get_tenant_by_handle(self, handle):
        # Mock tenant data
        mock_tenants = {
            '@test_store_1': {'id': 'tenant-1', 'instagram_handle': '@test_store_1', 'display_name': 'Test Store 1', 'status': 'active'},
            '@test_store_2': {'id': 'tenant-2', 'instagram_handle': '@test_store_2', 'display_name': 'Test Store 2', 'status': 'active'}
        }
        return mock_tenants.get(handle)

# Patch the database
sys.modules['database'] = type(sys)('database')
sys.modules['database'].db = MockDB()

from tenant_middleware import (
    tenant_context,
    TenantContext,
    HeaderBasedTenantStrategy,
    JWTBasedTenantStrategy,
    PathBasedTenantStrategy,
    SubdomainBasedTenantStrategy,
    get_current_tenant_id,
    require_tenant,
    with_tenant
)
from instagram_oauth import generate_session_token

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

def test_context_isolation():
    """Test that tenant context is properly isolated"""
    print("\n🔒 Testing Context Isolation...")
    
    try:
        # Set initial tenant
        tenant_context.set_tenant("tenant-1")
        initial_tenant = tenant_context.get_tenant_id()
        
        # Use with_tenant decorator
        @with_tenant("tenant-2")
        async def change_tenant_temporarily():
            temp_tenant = tenant_context.get_tenant_id()
            return temp_tenant
        
        loop = asyncio.get_event_loop()
        temp_result = loop.run_until_complete(change_tenant_temporarily())
        
        # Check that temporary tenant was set correctly
        if temp_result == "tenant-2":
            print("✅ Temporary tenant context set correctly")
        else:
            print(f"❌ Temporary tenant context failed: {temp_result}")
            return False
        
        # Check that original tenant is restored
        final_tenant = tenant_context.get_tenant_id()
        if final_tenant == initial_tenant:
            print("✅ Original tenant context restored")
        else:
            print(f"❌ Original tenant context not restored: {final_tenant} != {initial_tenant}")
            return False
        
        # Clear context
        tenant_context.clear_tenant()
        
        return True
        
    except Exception as e:
        print(f"❌ Context isolation test failed: {e}")
        return False

def test_multiple_strategies():
    """Test middleware with multiple identification strategies"""
    print("\n🔄 Testing Multiple Strategy Fallback...")
    
    try:
        from tenant_middleware import TenantMiddleware
        
        middleware = TenantMiddleware()
        loop = asyncio.get_event_loop()
        
        # Test JWT strategy (highest priority)
        user_data = {'id': '123', 'username': 'testuser'}
        jwt_token = generate_session_token(user_data, 'jwt-tenant')
        
        request_data = {
            'headers': {
                'Authorization': f'Bearer {jwt_token}',
                'X-Tenant-ID': 'header-tenant',  # This should be ignored
                'Host': 'subdomain.test.com'      # This should be ignored
            },
            'url': '/api/v1/tenant/path-tenant/data'  # This should be ignored
        }
        
        tenant_id = loop.run_until_complete(middleware.identify_tenant(request_data))
        
        if tenant_id == 'jwt-tenant':
            print("✅ JWT strategy has highest priority")
        else:
            print(f"❌ Strategy priority failed: {tenant_id}")
            return False
        
        # Test fallback to header when no JWT
        request_data = {
            'headers': {
                'X-Tenant-ID': 'header-tenant',
                'Host': 'subdomain.test.com'
            },
            'url': '/api/v1/tenant/path-tenant/data'
        }
        
        tenant_id = loop.run_until_complete(middleware.identify_tenant(request_data))
        
        if tenant_id == 'header-tenant':
            print("✅ Header strategy fallback working")
        else:
            print(f"❌ Header fallback failed: {tenant_id}")
            return False
        
        # Test fallback to path when no JWT or header
        request_data = {
            'headers': {
                'Host': 'subdomain.test.com'
            },
            'url': '/api/v1/tenant/path-tenant/data'
        }
        
        tenant_id = loop.run_until_complete(middleware.identify_tenant(request_data))
        
        if tenant_id == 'path-tenant':
            print("✅ Path strategy fallback working")
        else:
            print(f"❌ Path fallback failed: {tenant_id}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Multiple strategies test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🏢 IG-Shop-Agent Multi-Tenant Architecture Test Suite")
    print("   (Simplified - No Database Required)")
    print("=" * 60)
    
    tests = [
        ("Tenant Context Management", test_tenant_context),
        ("Tenant Identification Strategies", test_tenant_identification_strategies),
        ("Tenant Decorators", test_decorators),
        ("Context Isolation", test_context_isolation),
        ("Multiple Strategy Fallback", test_multiple_strategies)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            if test_func():
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
            print("✅ Multi-tenant architecture core logic is working correctly")
            print("ℹ️  Database-dependent features need real PostgreSQL for full testing")
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 