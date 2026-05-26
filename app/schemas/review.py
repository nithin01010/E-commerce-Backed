from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str]
    order_id: int


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    order_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
