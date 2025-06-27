"""
Business profile models.
"""
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class BusinessProfile(Base, TimestampMixin):
    """Business profile configuration in YAML format."""
    __tablename__ = "profiles"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), primary_key=True)
    yaml_profile = Column(JSON, nullable=False)  # YAML configuration stored as JSON
    
    # Relationships
    tenant = relationship("Tenant", back_populates="business_profile")
    
    @property
    def profile_data(self):
        """Get profile data as dict."""
        return self.yaml_profile or {}
    
    @profile_data.setter
    def profile_data(self, value):
        """Set profile data from dict."""
        self.yaml_profile = value
