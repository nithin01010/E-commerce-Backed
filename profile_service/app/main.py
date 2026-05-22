from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import customer, seller, address


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
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
    prefix='/address',
    tags=["Addresses"]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
