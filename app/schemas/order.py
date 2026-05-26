from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OrderCreate(BaseModel):
    address_id: int = Field(
        ...,
        description="The shipping address ID for the order"
    )


class OrderStatusUpdate(BaseModel):
    status: str


class OrderResponse(BaseModel):
    id: int
    quantity: int
    status: str
    total_amount: int
    address_id: int
    product_id: int
    customer_id: int
    seller_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
