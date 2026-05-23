from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
import redis.asyncio as redis

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

# Using HttpOnly Cookies for Auth

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, decode_responses=True
    )


async def get_redis():
    "Yields a Redis connection"
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> User:
    token = request.cookies.get("access_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated or token expired",
    )
    if not token:
        raise credentials_exception

    is_blacklisted = await redis_client.get(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked / logged out",
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
