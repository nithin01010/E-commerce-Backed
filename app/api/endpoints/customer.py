from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.schemas.profile import CustomerCreate, CustomerResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/onboarding",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
    )
async def create_customer_profile(
    profile_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=403,
            detail="Only customers can create a customer profile"
        )
    result = await db.execute(
        select(Customer).where(
            Customer.user_id == current_user.id
        )
    )

    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_customer = Customer(
        name=profile_in.name,
        phone_number=profile_in.phone_number,
        user_id=current_user.id
    )

    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)

    return new_customer


@router.get("/me", response_model=CustomerResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).where(
            Customer.user_id == current_user.id
        )
    )
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Please complete onboarding."
        )

    return customer
