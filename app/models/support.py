from .base import *


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="open", nullable=False)
    priority = Column(String(50), default="medium", nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="support_tickets")
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan")


class TicketReply(Base):
    __tablename__ = "ticket_replies"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("SupportTicket", back_populates="replies")
    user = relationship("User")

