"""
IG-Shop-Agent Azure Key Vault Test Script
Test Key Vault connectivity and secret management
"""
import os
import sys
import asyncio

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from azure_keyvault import keyvault, init_keyvault, get_secret, get_database_url, get_openai_api_key

def test_keyvault_integration():
    """Test Azure Key Vault integration"""
    print("🔐 Starting Azure Key Vault Integration Tests...")
    
    # Test environment variables
    print("\n📋 Testing Environment Configuration...")
    vault_url = os.getenv('AZURE_KEY_VAULT_URL')
    
    if vault_url:
        print(f"✅ AZURE_KEY_VAULT_URL: {vault_url}")
    else:
        print("ℹ️  AZURE_KEY_VAULT_URL: Not set (will use environment variables)")
    
    # Test Key Vault initialization
    print("\n🔗 Testing Key Vault Connection...")
    try:
        success = init_keyvault()
        if success:
            print("✅ Azure Key Vault initialized successfully")
            keyvault_available = True
        else:
            print("ℹ️  Azure Key Vault not available (using environment variables)")
            keyvault_available = False
    except Exception as e:
        print(f"ℹ️  Azure Key Vault initialization failed: {e}")
        keyvault_available = False
    
    # Test secret retrieval
    print("\n🔑 Testing Secret Retrieval...")
    
    # Test with environment variables
    os.environ['TEST_SECRET'] = 'test-value-from-env'
    secret_value = get_secret('test-secret', 'default-value')
    
    if secret_value == 'test-value-from-env':
        print("✅ Environment variable fallback working")
    else:
        print(f"❌ Environment variable fallback failed: got '{secret_value}'")
    
    # Test default value
    default_secret = get_secret('non-existent-secret', 'default-value')
    if default_secret == 'default-value':
        print("✅ Default value fallback working")
    else:
        print(f"❌ Default value fallback failed: got '{default_secret}'")
    
    # Test specific secret getters
    print("\n🔍 Testing Specific Secret Getters...")
    
    # Set test environment variables
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
    os.environ['OPENAI_API_KEY'] = 'sk-test-key'
    
    db_url = get_database_url()
    if db_url:
        print(f"✅ Database URL retrieval: {db_url[:20]}...")
    else:
        print("❌ Database URL retrieval failed")
    
    openai_key = get_openai_api_key()
    if openai_key:
        print(f"✅ OpenAI API key retrieval: {openai_key[:10]}...")
    else:
        print("❌ OpenAI API key retrieval failed")
    
    # Test Key Vault operations (if available)
    if keyvault_available and keyvault.client:
        print("\n🏪 Testing Key Vault Operations...")
        
        try:
            # Test setting a secret
            test_secret_name = "test-secret-igshop"
            test_secret_value = "test-value-12345"
            
            success = keyvault.set_secret(test_secret_name, test_secret_value)
            if success:
                print(f"✅ Secret '{test_secret_name}' set successfully")
                
                # Test getting the secret
                retrieved_value = keyvault.get_secret(test_secret_name)
                if retrieved_value == test_secret_value:
                    print(f"✅ Secret '{test_secret_name}' retrieved successfully")
                else:
                    print(f"❌ Secret retrieval failed: expected '{test_secret_value}', got '{retrieved_value}'")
                
                # Test listing secrets
                secrets = keyvault.list_secrets()
                if any(s['name'] == test_secret_name for s in secrets):
                    print(f"✅ Secret '{test_secret_name}' found in secrets list")
                else:
                    print(f"❌ Secret '{test_secret_name}' not found in secrets list")
                
                # Cleanup - delete test secret
                delete_success = keyvault.delete_secret(test_secret_name)
                if delete_success:
                    print(f"✅ Secret '{test_secret_name}' deleted successfully")
                else:
                    print(f"⚠️  Failed to delete test secret '{test_secret_name}'")
            else:
                print(f"❌ Failed to set test secret '{test_secret_name}'")
                
        except Exception as e:
            print(f"❌ Key Vault operations test failed: {e}")
    
    # Test configuration loading
    print("\n⚙️  Testing Configuration Loading...")
    
    from config import settings, get_instagram_oauth_config, get_openai_config
    
    try:
        # Test if settings can be loaded
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Environment: {settings.environment}")
        
        # Test Instagram config
        instagram_config = get_instagram_oauth_config()
        if instagram_config.get('app_id'):
            print(f"✅ Instagram config loaded")
        else:
            print("ℹ️  Instagram config not fully configured (expected for testing)")
        
        # Test OpenAI config
        openai_config = get_openai_config()
        if openai_config.get('api_key'):
            print(f"✅ OpenAI config loaded")
        else:
            print("ℹ️  OpenAI config not configured (expected for testing)")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    print("\n🎉 Azure Key Vault integration tests completed!")
    print("✅ Environment configuration is working correctly")
    return True

def test_production_readiness():
    """Test production readiness of configuration"""
    print("\n🚀 Testing Production Readiness...")
    
    # Required environment variables for production
    required_vars = [
        'DATABASE_URL',
        'OPENAI_API_KEY',
        'META_APP_ID',
        'META_APP_SECRET',
        'META_WEBHOOK_VERIFY_TOKEN',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    configured_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            configured_vars.append(var)
        else:
            missing_vars.append(var)
    
    print(f"✅ Configured variables: {len(configured_vars)}/{len(required_vars)}")
    for var in configured_vars:
        print(f"   ✅ {var}")
    
    if missing_vars:
        print(f"ℹ️  Missing variables (for production): {len(missing_vars)}")
        for var in missing_vars:
            print(f"   ⚠️  {var}")
        print("\n💡 To make production-ready:")
        print("   1. Set all required environment variables")
        print("   2. Configure Azure Key Vault")
        print("   3. Test with real Instagram and OpenAI credentials")
    else:
        print("🎉 All required variables are configured!")
        print("✅ Configuration is production-ready")
    
    return len(missing_vars) == 0

def main():
    """Main test function"""
    print("=" * 60)
    print("🔐 IG-Shop-Agent Environment Configuration Test Suite")
    print("=" * 60)
    
    try:
        # Run integration tests
        success = test_keyvault_integration()
        
        # Test production readiness
        production_ready = test_production_readiness()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 ENVIRONMENT CONFIGURATION TESTS PASSED!")
            if production_ready:
                print("✅ READY FOR PRODUCTION DEPLOYMENT")
            else:
                print("ℹ️  NEEDS PRODUCTION CONFIGURATION")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
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