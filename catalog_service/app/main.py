from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import category, product


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)
app.include_router(
    category.router,
    prefix='/categories',
    tags=["Categories"]
)

app.include_router(
    product.router,
    prefix='/products',
    tags=["Products"]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
