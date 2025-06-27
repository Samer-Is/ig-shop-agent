"""
Order management models.
"""
import enum
from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Text, Enum
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    """Order status types."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base, TimestampMixin):
    """Customer order."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=False)
    sku = Column(String(100), nullable=False)  # Denormalized for quick access
    qty = Column(Integer, nullable=False, default=1)
    customer = Column(String(255), nullable=False)  # Customer name from Instagram
    phone = Column(String(50))  # Customer phone if provided
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(DECIMAL(10, 3))  # Calculated total in JOD
    notes = Column(Text)  # Special instructions or notes
    
    # Relationships
    tenant = relationship("Tenant", back_populates="orders")
    catalog_item = relationship("CatalogItem", back_populates="orders")
