from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.seller import Seller
from app.schemas.profile import SellerCreate, SellerResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/onboarding",
    response_model=SellerResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_seller_profile(
    profile_in: SellerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # check if user is actulaly a seller

    if current_user.role_id != 2:
        raise HTTPException(
            status_code=403,
            detail="Only sellers can create a seller profile"
        )

    result = await db.execute(
        select(Seller).where(
            Seller.user_id == current_user.id
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    # create profile

    new_seller = Seller(
        name=profile_in.name,
        phone_number=profile_in.phone_number,
        user_id=current_user.id
    )

    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)

    return new_seller


@router.get('/me', response_model=SellerResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Seller).where(
            Seller.user_id == current_user.id
        )
    )

    seller = result.scalars().first()

    if not seller:
        raise HTTPException(
            status_code=404,
            detail="Seller Profile not found. Please complete onboarding"
        )
    return seller
