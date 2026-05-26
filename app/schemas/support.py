from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TicketReplyCreate(BaseModel):
    message: str


class TicketReplyResponse(BaseModel):
    id: int
    message: str
    is_admin: bool
    ticket_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: Optional[str]


class SupportTicketUpdate(BaseModel):
    status: Optional[str]
    priority: Optional[str]


class SupportTicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    priority: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List[TicketReplyResponse] = []

    class Config:
        from_attributes = True

