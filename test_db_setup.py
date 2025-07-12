#!/usr/bin/env python3
"""
Test script to set up test data in the database
"""
import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_database

async def setup_test_data():
    """Set up test data in the database"""
    try:
        print("🔄 Connecting to database...")
        db = await get_database()
        
        print("📊 Checking existing users...")
        users = await db.fetch_all('SELECT * FROM users LIMIT 3')
        print(f"Found {len(users)} users:", users)
        
        print("👤 Creating test user...")
        await db.execute_query('''
            INSERT INTO users (id, instagram_handle, instagram_page_id, instagram_connected, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            ON CONFLICT (id) DO UPDATE SET
                instagram_handle = EXCLUDED.instagram_handle,
                instagram_page_id = EXCLUDED.instagram_page_id,
                instagram_connected = EXCLUDED.instagram_connected
        ''', 'test-user-123', 'test_user', 'test-page-123', True)
        print("✅ Test user created/updated")
        
        print("📦 Creating test catalog items...")
        catalog_items = [
            ('test-product-1', 'Test Product 1', 'A great test product', 29.99, 'https://example.com/image1.jpg', True),
            ('test-product-2', 'Test Product 2', 'Another test product', 49.99, 'https://example.com/image2.jpg', True),
            ('test-product-3', 'Test Product 3', 'Premium test product', 99.99, 'https://example.com/image3.jpg', True)
        ]
        
        for item_id, name, description, price, image_url, available in catalog_items:
            await db.execute_query('''
                INSERT INTO catalog_items (id, user_id, sku, name, description, price_jod, media_url, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    price_jod = EXCLUDED.price_jod,
                    media_url = EXCLUDED.media_url
            ''', item_id, 'test-user-123', item_id, name, description, price, image_url)
        
        print("✅ Test catalog items created")
        
        print("🛒 Creating test orders...")
        await db.execute_query('''
            INSERT INTO orders (id, user_id, sku, qty, customer, phone, delivery_address, total_amount, status, notes, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            ON CONFLICT (id) DO UPDATE SET
                customer = EXCLUDED.customer,
                status = EXCLUDED.status
        ''', 'test-order-1', 'test-user-123', 'test-product-1', 2, 'Test Customer', '+1234567890', '123 Test St, Test City', 79.98, 'pending', 'Test order with 2 items')
        
        print("✅ Test order created")
        
        print("📋 Verifying test data...")
        catalog = await db.fetch_all('SELECT * FROM catalog_items WHERE user_id = $1', 'test-user-123')
        print(f"📦 Catalog items for test user: {len(catalog)}")
        
        orders = await db.fetch_all('SELECT * FROM orders WHERE user_id = $1', 'test-user-123')
        print(f"🛒 Orders for test user: {len(orders)}")
        
        print("✅ Test data setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_test_data()) 