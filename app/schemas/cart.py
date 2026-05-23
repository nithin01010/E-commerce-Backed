from pydantic import BaseModel
from app.schemas.product import ProductResponse


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    customer_id: int
    quantity: int

    product: ProductResponse

    class Config:
        from_attributes = True


class CartItemUpdate(BaseModel):
    quantity: int
