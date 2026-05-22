from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis
import json

from app.core.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryResponse, CatergoryCreate
from app.api.deps import get_current_user, get_redis

router = APIRouter()


@router.post(
    '/',
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_in: CatergoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    if current_user.role_id != 3:
        raise HTTPException(
            status_code=403,
            detail="Only admins can mange categories"
        )
    result = await db.execute(
        select(Category).where(
            Category.name == category_in.name
        )
    )
    category = result.scalars().first()
    if category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category_in.name
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    await redis_client.delete("categories_list")

    return new_category


@router.get('/')
async def get_categories(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    # Check in redis and cache it
    cached_categories = await redis_client.get("categories_list")
    if cached_categories:
        return json.loads(cached_categories)

    # if not in redis

    result = await db.execute(select(Category))
    categories = result.scalars().all()

    categories_data = [{"id": c.id, "name": c.name} for c in categories]

    await redis_client.setex(
        "categories_list",
        60 * 60 * 12,
        json.dumps(categories_data)
    )
    return categories_data
