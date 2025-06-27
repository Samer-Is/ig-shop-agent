"""
Catalog and inventory models.
"""
from decimal import Decimal
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Text, JSON
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class CatalogItem(Base, TimestampMixin):
    """Product catalog item."""
    __tablename__ = "catalog_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sku = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    price_jod = Column(DECIMAL(10, 3), nullable=False)  # Jordanian Dinars with 3 decimal places
    media_url = Column(Text)  # URL to product image/video
    extras = Column(JSON)  # Additional product details (sizes, colors, description, etc.)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="catalog_items")
    orders = relationship("Order", back_populates="catalog_item")
    
    # Composite index for tenant_id + sku uniqueness
    __table_args__ = (
        {'extend_existing': True},
    )
