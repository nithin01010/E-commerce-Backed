from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import auth


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
