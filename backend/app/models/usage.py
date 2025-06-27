"""
Usage and billing models.
"""
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship

from .base import Base


class UsageStats(Base):
    """Daily usage statistics for billing."""
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    openai_cost_usd = Column(DECIMAL(10, 4), default=0.0000)  # Daily OpenAI costs
    meta_messages = Column(Integer, default=0)  # Number of messages processed
    total_tokens = Column(Integer, default=0)  # Total tokens used
    
    # Relationships
    tenant = relationship("Tenant", back_populates="usage_stats")
    
    # Composite index for tenant and date
    __table_args__ = (
        {'extend_existing': True},
    )
