"""
Conversation and messaging models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Conversation(Base):
    """Conversation messages with Instagram users."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sender = Column(String(255), nullable=False)  # Instagram user ID or handle
    text = Column(Text, nullable=False)  # Message content
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Timestamp
    tokens_in = Column(Integer, default=0)  # OpenAI input tokens used
    tokens_out = Column(Integer, default=0)  # OpenAI output tokens used
    message_type = Column(String(50), default="text")  # text, image, video, audio
    is_ai_response = Column(String(10), default="false")  # "true" if AI generated, "false" if human
    instagram_message_id = Column(String(100))  # Instagram message ID for deduplication
    
    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    
    # Index for efficient conversation retrieval
    __table_args__ = (
        {'extend_existing': True},
    )
