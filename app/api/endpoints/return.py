from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.seller import Seller
from app.models.order import Order
from app.models.return_request import Return
from app.schemas.return_request import ReturnCreate, ReturnUpdate
from app.schemas.return_request import ReturnResponse
from app.api.deps import get_current_user

router = APIRouter()


# -----------------------------HELPER FUNCTIONS-------------------------------


async def get_customer_profile(db: AsyncSession, user_id: int) -> Customer:
    result = await db.execute(
        select(Customer).where(Customer.user_id == user_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found."
        )
    return customer


async def get_seller_profile(db: AsyncSession, user_id: int) -> Seller:
    result = await db.execute(
        select(Seller).where(Seller.user_id == user_id)
    )
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller profile not found."
        )
    return seller


def check_is_customer(role_id):
    if role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can request returns."
        )


def check_is_seller(role_id):
    if role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can update return request status."
        )


def check_return_exists(return_req):
    if not return_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found."
        )


async def get_customer_order(
    db: AsyncSession,
    order_id: int,
    customer_id: int
) -> Order:
    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_id == customer_id
        )
    )
    order = order_result.scalars().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or does not belong to you."
        )
    return order


async def verify_seller_order(
    db: AsyncSession,
    order_id: int,
    seller_id: int
) -> Order:
    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.seller_id == seller_id
        )
    )
    order = order_result.scalars().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this order."
        )
    return order


async def check_return_already_submitted(db: AsyncSession, order_id: int):
    existing_result = await db.execute(
        select(Return).where(Return.order_id == order_id)
    )
    existing_return = existing_result.scalars().first()
    if existing_return:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="""A return request has already been
            submitted for this order."""
        )


async def get_return_req(db: AsyncSession, return_id: int) -> Return:
    result = await db.execute(
        select(Return).where(Return.id == return_id)
    )
    return_req = result.scalars().first()
    check_return_exists(return_req)
    return return_req


# -----------------------------------------------------------------------------


@router.post(
    "/",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_return_request(
    return_in: ReturnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_customer(current_user.role_id)
    customer = await get_customer_profile(db, current_user.id)

    # Fetch and verify customer's order ownership
    await get_customer_order(db, return_in.order_id, customer.id)

    # Check for duplicate return requests
    await check_return_already_submitted(db, return_in.order_id)

    new_return = Return(
        order_id=return_in.order_id,
        status="pending",
        comment=return_in.comment
    )
    db.add(new_return)
    await db.commit()
    await db.refresh(new_return)
    return new_return


@router.get("/", response_model=List[ReturnResponse])
async def list_return_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id == 1:
        # Customer: see returns for their own orders
        customer = await get_customer_profile(db, current_user.id)
        result = await db.execute(
            select(Return).join(Order).where(Order.customer_id == customer.id)
        )
    elif current_user.role_id == 2:
        # Seller: see returns for orders of their products
        seller = await get_seller_profile(db, current_user.id)
        result = await db.execute(
            select(Return).join(Order).where(Order.seller_id == seller.id)
        )
    elif current_user.role_id == 3:
        # Admin: see all return requests
        result = await db.execute(select(Return))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not authorized to view return requests."
        )
    return result.scalars().all()


@router.get("/{return_id}", response_model=ReturnResponse)
async def get_return_request(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return_req = await get_return_req(db, return_id)

    # Verify access permission
    if current_user.role_id == 1:
        customer = await get_customer_profile(db, current_user.id)
        await get_customer_order(db, return_req.order_id, customer.id)
    elif current_user.role_id == 2:
        seller = await get_seller_profile(db, current_user.id)
        await verify_seller_order(db, return_req.order_id, seller.id)
    elif current_user.role_id != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not authorized to view return requests."
        )

    return return_req


@router.put("/{return_id}/status", response_model=ReturnResponse)
async def update_return_status(
    return_id: int,
    return_update: ReturnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_seller(current_user.role_id)
    seller = await get_seller_profile(db, current_user.id)

    return_req = await get_return_req(db, return_id)

    # Verify that the order belongs to this seller
    order = await verify_seller_order(db, return_req.order_id, seller.id)

    return_req.status = return_update.status
    if return_update.comment:
        return_req.comment = return_update.comment

    # If approved, update the corresponding order status to "Returned"
    if return_update.status.lower() == "approved":
        order.status = "Returned"

    await db.commit()
    await db.refresh(return_req)
    return return_req
