"""
Vector Search Service using PostgreSQL pgvector extension.
Replaces Azure AI Search for cost optimization.
"""
import asyncpg
import openai
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncAzureOpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class VectorSearch:
    """Vector search using PostgreSQL pgvector extension."""
    
    def __init__(self):
        """Initialize vector search service."""
        self.openai_client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version="2024-02-01"
        ) if settings.azure_openai_endpoint else openai.AsyncOpenAI(
            api_key=settings.azure_openai_api_key or settings.openai_api_key
        )
        
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.embedding_model_name,
                input=text.replace("\n", " ")
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * 1536  # Return zero vector as fallback
    
    async def init_vector_tables(self):
        """Initialize vector search tables and indexes."""
        try:
            conn = await asyncpg.connect(settings.database_url)
            
            # Create pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create products vector table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS product_vectors (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES catalog_items(id) ON DELETE CASCADE
                );
            """)
            
            # Create vector index for cosine similarity
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS product_vectors_embedding_idx 
                ON product_vectors USING ivfflat (embedding vector_cosine_ops);
            """)
            
            # Create knowledge base vector table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_vectors (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    document_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                    FOREIGN KEY (document_id) REFERENCES kb_documents(id) ON DELETE CASCADE
                );
            """)
            
            # Create vector index for knowledge base
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS knowledge_vectors_embedding_idx 
                ON knowledge_vectors USING ivfflat (embedding vector_cosine_ops);
            """)
            
            await conn.close()
            logger.info("Vector tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector tables: {e}")
    
    async def add_product(self, tenant_id: int, product_data: Dict[str, Any]) -> bool:
        """Add product to vector search index."""
        try:
            # Prepare content for embedding
            content = f"{product_data['name']} {product_data.get('description', '')}"
            
            # Generate embedding
            embedding = await self.get_embedding(content)
            
            # Store in database
            conn = await asyncpg.connect(settings.database_url)
            
            # Delete existing vector for this product
            await conn.execute(
                "DELETE FROM product_vectors WHERE tenant_id = $1 AND product_id = $2",
                tenant_id, product_data['id']
            )
            
            # Insert new vector
            await conn.execute("""
                INSERT INTO product_vectors (tenant_id, product_id, content, embedding)
                VALUES ($1, $2, $3, $4)
            """, tenant_id, product_data['id'], content, embedding)
            
            await conn.close()
            logger.info(f"Added product {product_data['id']} to vector index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding product to vector index: {e}")
            return False
    
    async def search_products(
        self, 
        tenant_id: int, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search products using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.get_embedding(query)
            
            conn = await asyncpg.connect(settings.database_url)
            
            # Search using cosine similarity
            results = await conn.fetch("""
                SELECT 
                    pv.product_id,
                    pv.content,
                    ci.name,
                    ci.description,
                    ci.price_jod,
                    ci.sku,
                    ci.category,
                    1 - (pv.embedding <=> $1) as similarity
                FROM product_vectors pv
                JOIN catalog_items ci ON pv.product_id = ci.id
                WHERE pv.tenant_id = $2
                AND 1 - (pv.embedding <=> $1) > $3
                ORDER BY pv.embedding <=> $1
                LIMIT $4
            """, query_embedding, tenant_id, similarity_threshold, limit)
            
            await conn.close()
            
            # Format results
            products = []
            for result in results:
                products.append({
                    "product_id": result["product_id"],
                    "name": result["name"],
                    "description": result["description"],
                    "price_jod": float(result["price_jod"]),
                    "sku": result["sku"],
                    "category": result["category"],
                    "similarity": float(result["similarity"]),
                    "content": result["content"]
                })
            
            logger.info(f"Found {len(products)} products for query: {query}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    async def add_knowledge_document(
        self, 
        tenant_id: int, 
        document_id: int, 
        content: str,
        chunk_size: int = 1000
    ) -> bool:
        """Add knowledge document to vector search index with chunking."""
        try:
            conn = await asyncpg.connect(settings.database_url)
            
            # Delete existing vectors for this document
            await conn.execute(
                "DELETE FROM knowledge_vectors WHERE tenant_id = $1 AND document_id = $2",
                tenant_id, document_id
            )
            
            # Split content into chunks
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            # Process each chunk
            for chunk in chunks:
                if chunk.strip():  # Skip empty chunks
                    embedding = await self.get_embedding(chunk)
                    
                    await conn.execute("""
                        INSERT INTO knowledge_vectors (tenant_id, document_id, content, embedding)
                        VALUES ($1, $2, $3, $4)
                    """, tenant_id, document_id, chunk, embedding)
            
            await conn.close()
            logger.info(f"Added knowledge document {document_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error adding knowledge document: {e}")
            return False
    
    async def search_knowledge(
        self, 
        tenant_id: int, 
        query: str, 
        limit: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.get_embedding(query)
            
            conn = await asyncpg.connect(settings.database_url)
            
            # Search using cosine similarity
            results = await conn.fetch("""
                SELECT 
                    kv.document_id,
                    kv.content,
                    kd.title,
                    kd.file_type,
                    1 - (kv.embedding <=> $1) as similarity
                FROM knowledge_vectors kv
                JOIN kb_documents kd ON kv.document_id = kd.id
                WHERE kv.tenant_id = $2
                AND 1 - (kv.embedding <=> $1) > $3
                ORDER BY kv.embedding <=> $1
                LIMIT $4
            """, query_embedding, tenant_id, similarity_threshold, limit)
            
            await conn.close()
            
            # Format results
            documents = []
            for result in results:
                documents.append({
                    "document_id": result["document_id"],
                    "title": result["title"],
                    "content": result["content"],
                    "file_type": result["file_type"],
                    "similarity": float(result["similarity"])
                })
            
            logger.info(f"Found {len(documents)} knowledge chunks for query: {query}")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def delete_product_vectors(self, tenant_id: int, product_id: int) -> bool:
        """Delete vectors for a specific product."""
        try:
            conn = await asyncpg.connect(settings.database_url)
            await conn.execute(
                "DELETE FROM product_vectors WHERE tenant_id = $1 AND product_id = $2",
                tenant_id, product_id
            )
            await conn.close()
            logger.info(f"Deleted vectors for product {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting product vectors: {e}")
            return False
    
    async def delete_knowledge_vectors(self, tenant_id: int, document_id: int) -> bool:
        """Delete vectors for a specific knowledge document."""
        try:
            conn = await asyncpg.connect(settings.database_url)
            await conn.execute(
                "DELETE FROM knowledge_vectors WHERE tenant_id = $1 AND document_id = $2",
                tenant_id, document_id
            )
            await conn.close()
            logger.info(f"Deleted vectors for knowledge document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting knowledge vectors: {e}")
            return False
    
    async def get_stats(self, tenant_id: int) -> Dict[str, int]:
        """Get vector search statistics for a tenant."""
        try:
            conn = await asyncpg.connect(settings.database_url)
            
            # Count product vectors
            product_count = await conn.fetchval(
                "SELECT COUNT(*) FROM product_vectors WHERE tenant_id = $1",
                tenant_id
            )
            
            # Count knowledge vectors
            knowledge_count = await conn.fetchval(
                "SELECT COUNT(*) FROM knowledge_vectors WHERE tenant_id = $1",
                tenant_id
            )
            
            await conn.close()
            
            return {
                "product_vectors": product_count,
                "knowledge_vectors": knowledge_count,
                "total_vectors": product_count + knowledge_count
            }
            
        except Exception as e:
            logger.error(f"Error getting vector stats: {e}")
            return {"product_vectors": 0, "knowledge_vectors": 0, "total_vectors": 0} 