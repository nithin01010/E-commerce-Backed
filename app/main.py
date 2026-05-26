from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import auth, customer, seller, address
from app.api.endpoints import category, cart, order, review, product, support, admin
from fastapi.middleware.cors import CORSMiddleware
import importlib

return_endpoint = importlib.import_module("app.api.endpoints.return")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    customer.router,
    prefix='/customer',
    tags=["Customers"]
)

app.include_router(
    seller.router,
    prefix='/seller',
    tags=["Sellers"]
)


app.include_router(
    address.router,
    prefix="/addresses",
    tags=["Addresses"]
)

app.include_router(
    category.router,
    prefix='/categories',
    tags=["Categories"]
)

app.include_router(
    cart.router,
    prefix="/cart",
    tags=["Cart"]
)

app.include_router(
    order.router,
    prefix="/orders",
    tags=["Orders"]
)

app.include_router(
    review.router,
    prefix="/reviews",
    tags=["Reviews"]
)

app.include_router(
    product.router,
    prefix="/products",
    tags=["Products"]
)

app.include_router(
    return_endpoint.router,
    prefix="/returns",
    tags=["Returns"]
)

app.include_router(
    support.router,
    prefix="/support",
    tags=["Support"]
)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

