from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.category import Category
from app.models.seller import Seller
from app.models.product import Product, ProductImage
from app.schemas.product import ProductCreate, ProductImageResponse
from app.schemas.product import ProductResponse


router = APIRouter()


# -----------------------------HELPER FUNCTIOSNS-------------------------------


async def get_seller_profile(db: AsyncSession, user_id: int) -> Seller:
    result = await db.execute(select(Seller).where(Seller.user_id == user_id))
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found."
        )
    return seller


def check_is_seller(role_id):
    if role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create products",
        )


def check_category_exists(category):
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )


async def check_product_exists(db: AsyncSession, name: str, seller_id: int):
    result = await db.execute(
        select(Product).where(Product.name == name, Product.seller_id == seller_id)
    )
    product = result.scalars().first()
    if product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists in your store",
        )


def check_product_exists1(product):
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )


async def get_product(db, product_id, seller_id):
    prod = await db.execute(
        select(Product)
        .where(Product.id == product_id, Product.seller_id == seller_id)
        .options(Product.images)
    )
    product = prod.scalars().first()
    check_product_exists1(product)
    return product


# ----------------------------------------------------------------------------------


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_is_seller(current_user.role_id)

    seller = await get_seller_profile(db, current_user.id)
    cat = await db.execute(
        select(Category).where(Category.id == product_in.category_id)
    )
    category = cat.scalars().first()
    check_category_exists(category)

    await check_product_exists(db, product_in.name, seller.id)

    new_prod = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        category_id=product_in.category_id,
        seller_id=seller.id,
    )

    db.add(new_prod)
    await db.commit()
    await db.refresh(new_prod)
    return new_prod


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_is_seller(current_user.role_id)

    seller = await get_seller_profile(db, current_user.id)
    product = await get_product(product_id, seller.id)

    cat = await db.execute(
        select(Category).where(Category.id == product_in.category_id)
    )
    category = cat.scalars().first()
    check_category_exists(category)

    product.name = product_in.name
    product.description = product_in.description
    product.price = product_in.price
    product.stock = product_in.stock
    product.category_id = product_in.category_id

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_is_seller(current_user.role_id)

    seller = await get_seller_profile(db, current_user.id)

    product = await get_product(db, product_id, seller.id)

    await db.delete(product)
    await db.commit()
    return


@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_product_image(
    product_id: int,
    image_url: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_is_seller(current_user.role_id)

    seller = await get_seller_profile(db, current_user.id)
    product = await get_product(db, product_id, seller.id)

    new_image = ProductImage(url=image_url, product_id=product_id)
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image
