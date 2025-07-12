#!/usr/bin/env python3
"""
Debug script to test catalog functionality
"""
import asyncio
import sys
import os
import traceback

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_database

async def debug_catalog():
    """Debug catalog functionality"""
    try:
        print("🔄 Connecting to database...")
        db = await get_database()
        
        user_id = 'test-user-123'
        print(f"👤 Testing for user: {user_id}")
        
        print("📊 Fetching catalog items...")
        items = await db.fetch_all("""
            SELECT id, sku, name, description, price_jod, media_url, product_link, 
                   category, stock_quantity, extras, created_at, updated_at
            FROM catalog_items 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """, user_id)
        
        print(f"📦 Found {len(items)} catalog items:")
        for item in items:
            print(f"  - {item['name']} (SKU: {item['sku']}, Price: {item['price_jod']} JOD)")
        
        print("✅ Catalog debug complete!")
        
    except Exception as e:
        print(f"❌ Error debugging catalog: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_catalog()) 