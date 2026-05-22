from pydantic import BaseModel
from typing import Optional


class AddressCreate(BaseModel):
    full_name: str
    phone: str
    street: str
    city: str
    state: str
    pincode: str
    country: Optional[str] = "India"
    is_default: Optional[bool] = False


class AddressResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    street: str
    city: str
    state: str
    pincode: str
    country: str
    is_default: bool
    customer_id: Optional[int] = None
    seller_id: Optional[int] = None

    class Config:
        from_attributes = True
