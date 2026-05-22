from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import redis.asyncio as redis

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.core.security import create_access_token
from app.api.deps import get_redis, get_current_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registerd")

    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password=hashed_pwd,
        role_id=user_in.role_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login")
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(
        User.where(User.email) == form_data.username
        ))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # creeate JWT token
    access_token_expire = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expire
    )

    # HTTP Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60
    )

    return {"message": "Successfully logged in", "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    token = request.cookies.get("access_token")
    # Add token to Redis blacklist with a TTL equal to token expiration
    if token:
        await redis_client.setex(
            f"blacklist:{token}",
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "true"
        )

    # Clear the cookie
    response.delete_cookie("access_token")

    return {"message": "Successfully logged out"}
