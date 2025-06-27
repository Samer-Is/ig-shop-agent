"""
Tenant and user management models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base, TimestampMixin


class PlanType(str, enum.Enum):
    """Subscription plan types."""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserRole(str, enum.Enum):
    """User role types."""
    ADMIN = "admin"
    MERCHANT = "merchant"
    SUPPORT = "support"


class Tenant(Base, TimestampMixin):
    """Tenant model for multi-tenancy."""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    instagram_handle = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    plan = Column(Enum(PlanType), default=PlanType.BASIC, nullable=False)
    
    # Enable Row-Level Security
    __table_args__ = {
        'postgresql_rlspolicy': {
            'name': 'tenant_isolation',
            'cmd': 'ALL',
            'role': 'authenticated',
            'using': 'tenant_id = current_setting(\'app.current_tenant\')::int'
        }
    }
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    catalog_items = relationship("CatalogItem", back_populates="tenant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="tenant", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="tenant", cascade="all, delete-orphan")
    business_profile = relationship("BusinessProfile", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStats", back_populates="tenant", cascade="all, delete-orphan")
    meta_token = relationship("MetaToken", back_populates="tenant", uselist=False, cascade="all, delete-orphan")


class User(Base, TimestampMixin):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.MERCHANT, nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")


class MetaToken(Base):
    """Meta API tokens for Instagram integration."""
    __tablename__ = "meta_tokens"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), primary_key=True)
    access_token = Column(Text, nullable=False)  # Encrypted
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="meta_token")
