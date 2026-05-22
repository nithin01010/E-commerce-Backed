from pydantic import BaseModel
from typing import Optional


class ProductImageResponse(BaseModel):
    id: int
    url: str

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    is_verified: bool
    status: str
    rating: Optional[float]
    seller_id: int
    category_id: int

    images: list[ProductImageResponse] = []

    class Config:
        from_attributes = True
