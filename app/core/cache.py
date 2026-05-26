import json
from typing import Any, Optional
import redis.asyncio as redis


async def get_cached(
    redis_client: redis.Redis,
    key: str
) -> Optional[Any]:
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def set_cache(
    redis_client: redis.Redis,
    key: str,
    value: Any,
    ttl: int = 60
) -> None:
    await redis_client.setex(key, ttl, json.dumps(value))


async def invalidate_pattern(
    redis_client: redis.Redis,
    pattern: str
) -> None:
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)


def serialize_product(p) -> dict:
    """Convert a product into json-serializable dict

    Args:
        p (Product)

    Returns:
        dict: encode the Product
    """
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "is_verified": p.is_verified,
        "status": p.status,
        "rating": p.rating,
        "seller_id": p.seller_id,
        "category_id": p.category_id,
        "images": [{"id": img.id, "url": img.url} for img in p.images]
    }


def serialize_review(r) -> dict:

    return {
        "id": r.id,
        "rating": r.rating,
        "comment": r.comment,
        "order_id": r.order_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }
