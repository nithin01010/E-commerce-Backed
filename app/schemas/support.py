from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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

    class Config:
        from_attributes = True
