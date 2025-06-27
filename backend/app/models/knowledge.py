"""
Knowledge base models for vector search.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class KnowledgeDocument(Base, TimestampMixin):
    """Knowledge base document with vector indexing."""
    __tablename__ = "kb_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    file_uri = Column(Text, nullable=False)  # Blob storage URI
    title = Column(String(255), nullable=False)
    vector_id = Column(String(100))  # Reference to Azure AI Search document ID
    content_type = Column(String(50))  # pdf, doc, txt, url, etc.
    file_size = Column(Integer)  # File size in bytes
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Relationships
    tenant = relationship("Tenant", back_populates="knowledge_documents")
