from pydantic import BaseModel
from typing import Optional


# ----------------------- CUSTOMER ------------------------
class CustomerCreate(BaseModel):
    name: str
    phone_number: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    is_active: bool
    user_id: int

    class Config:
        from_attributes = True


# ----------------------- SELLER ---------------------------
class SellerCreate(BaseModel):
    name: str
    phone_number: str


class SellerResponse(BaseModel):
    id: int
    name: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    status: Optional[str]
    rating: Optional[float]
    earnings: float
    is_verified: bool
    user_id: int

    class Config:
        from_attributes = True
