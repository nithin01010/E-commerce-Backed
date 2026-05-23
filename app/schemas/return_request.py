from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReturnCreate(BaseModel):
    order_id: int
    comment: Optional[str]


class ReturnUpdate(BaseModel):
    status: str
    comment: Optional[str]


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    status: str
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
