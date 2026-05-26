from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.seller import Seller
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
from app.models.support import SupportTicket, TicketReply
from app.api.deps import get_current_user
from app.schemas.profile import CustomerResponse, SellerResponse
from app.schemas.product import ProductResponse
from app.schemas.review import ReviewResponse
from app.schemas.order import OrderResponse
from app.schemas.support import SupportTicketResponse, TicketReplyCreate, TicketReplyResponse
from app.core.config import settings

router = APIRouter()


# -----------------------------HELPER FUNCTIONS-------------------------------


def check_is_admin(role_id: int):
    if role_id != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )


async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer:
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


async def get_seller_by_id(db: AsyncSession, seller_id: int) -> Seller:
    result = await db.execute(
        select(Seller).where(Seller.id == seller_id)
    )
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )
    return seller


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product:
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.images))
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


# -----------------------------------------------------------------------------


@router.put("/customers/{id}/block")
async def block_customer(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)

    customer = await get_customer_by_id(db, id)
    user = await get_user_by_id(db, customer.user_id)

    customer.is_active = False
    user.is_active = False

    await db.commit()
    return {"message": f"Customer '{customer.name or id}' has been blocked successfully."}


@router.put("/customers/{id}/unblock")
async def unblock_customer(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)

    customer = await get_customer_by_id(db, id)
    user = await get_user_by_id(db, customer.user_id)

    customer.is_active = True
    user.is_active = True

    await db.commit()
    return {"message": f"Customer '{customer.name or id}' has been unblocked successfully."}


@router.put("/sellers/{id}/block")
async def block_seller(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)

    seller = await get_seller_by_id(db, id)
    user = await get_user_by_id(db, seller.user_id)

    seller.is_active = False
    user.is_active = False

    await db.commit()
    return {"message": f"Seller '{seller.name or id}' has been blocked successfully."}


@router.put("/sellers/{id}/unblock")
async def unblock_seller(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)

    seller = await get_seller_by_id(db, id)
    user = await get_user_by_id(db, seller.user_id)
    seller.is_active = True
    user.is_active = True

    await db.commit()
    return {"message": f"Seller '{seller.name or id}' has been unblocked successfully."}


@router.put("/products/{id}/verify")
async def verify_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    product = await get_product_by_id(db, id)
    product.is_verified = True
    product.status = "active"
    
    await db.commit()
    return {"message": f"Product '{product.name}' has been verified successfully."}


@router.put("/products/{id}/block")
async def block_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    product = await get_product_by_id(db, id)
    product.is_verified = False
    product.status = "blocked"
    
    await db.commit()
    return {"message": f"Product '{product.name}' has been blocked successfully."}


@router.put("/products/{id}/unblock")
async def unblock_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    product = await get_product_by_id(db, id)
    product.is_verified = True
    product.status = "active"
    
    await db.commit()
    return {"message": f"Product '{product.name}' has been unblocked successfully."}


# ----------------------------- DIRECTORY & SEARCH ENDPOINTS -----------------------------


@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    query = select(Customer)
    if search:
        if search.isdigit():
            query = query.where((Customer.id == int(search)) | (Customer.name.ilike(f"%{search}%")))
        else:
            query = query.where(Customer.name.ilike(f"%{search}%"))
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/customers/{id}", response_model=CustomerResponse)
async def get_customer_details(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    customer = await get_customer_by_id(db, id)
    return customer


@router.get("/sellers", response_model=List[SellerResponse])
async def list_sellers(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    query = select(Seller)
    if search:
        if search.isdigit():
            query = query.where((Seller.id == int(search)) | (Seller.name.ilike(f"%{search}%")))
        else:
            query = query.where(Seller.name.ilike(f"%{search}%"))
            
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sellers/pending", response_model=List[SellerResponse])
async def list_pending_sellers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(
        select(Seller).where(Seller.is_verified == False, Seller.status == "pending")
    )
    return result.scalars().all()


@router.get("/sellers/{id}", response_model=SellerResponse)
async def get_seller_details(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    seller = await get_seller_by_id(db, id)
    return seller


@router.put("/sellers/{id}/approve")
async def approve_seller(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    seller = await get_seller_by_id(db, id)
    seller.is_verified = True
    seller.status = "approved"
    await db.commit()
    return {"message": f"Seller '{seller.name}' has been approved successfully."}


@router.put("/sellers/{id}/reject")
async def reject_seller(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    seller = await get_seller_by_id(db, id)
    seller.is_verified = False
    seller.status = "rejected"
    await db.commit()
    return {"message": f"Seller '{seller.name}' has been rejected successfully."}


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    query = select(Product).options(selectinload(Product.images))
    if search:
        if search.isdigit():
            query = query.where((Product.id == int(search)) | (Product.name.ilike(f"%{search}%")))
        else:
            query = query.where(Product.name.ilike(f"%{search}%"))
            
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/products/pending", response_model=List[ProductResponse])
async def list_pending_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(
        select(Product)
        .where(Product.is_verified == False, Product.status == "under verfication")
        .options(selectinload(Product.images))
    )
    return result.scalars().all()


@router.get("/products/{id}", response_model=ProductResponse)
async def get_product_details(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    product = await get_product_by_id(db, id)
    return product


# ----------------------------- REVIEW MODERATION -----------------------------


@router.get("/reviews", response_model=List[ReviewResponse])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(select(Review))
    return result.scalars().all()


@router.delete("/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(select(Review).where(Review.id == id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    await db.delete(review)
    await db.commit()
    return None


# ----------------------------- ORDER AUDITING -----------------------------


@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    query = select(Order)
    if status_filter:
        query = query.where(Order.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/orders/{id}", response_model=OrderResponse)
async def get_order_details(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(select(Order).where(Order.id == id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


# ----------------------------- SUPPORT TICKETS REPLY -----------------------------


@router.post("/support/tickets/{id}/reply", response_model=TicketReplyResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_ticket(
    id: int,
    reply_in: TicketReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    t_result = await db.execute(select(SupportTicket).where(SupportTicket.id == id))
    ticket = t_result.scalars().first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found"
        )
        
    new_reply = TicketReply(
        message=reply_in.message,
        is_admin=True,
        ticket_id=id,
        user_id=current_user.id
    )
    db.add(new_reply)
    await db.commit()
    await db.refresh(new_reply)
    return new_reply


# ----------------------------- CASCADE DELETIONS -----------------------------


@router.delete("/customers/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    customer = await get_customer_by_id(db, id)
    user = await get_user_by_id(db, customer.user_id)
    
    await db.delete(customer)
    await db.delete(user)
    await db.commit()
    return None


@router.delete("/sellers/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    seller = await get_seller_by_id(db, id)
    user = await get_user_by_id(db, seller.user_id)
    
    await db.delete(seller)
    await db.delete(user)
    await db.commit()
    return None


@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    product = await get_product_by_id(db, id)
    await db.delete(product)
    await db.commit()
    return None


# ----------------------------- ANALYTICS REPORTS -----------------------------


@router.get("/reports/revenue")
async def get_revenue_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    result = await db.execute(select(func.sum(Order.total_amount)))
    total_sales = result.scalar() or 0
    
    commission_rate = settings.PLATFORM_COMMISSION_PERCENT
    platform_earnings = float(total_sales) * commission_rate
    
    return {
        "total_sales": float(total_sales),
        "commission_rate": commission_rate,
        "platform_earnings": platform_earnings
    }


@router.get("/reports/orders")
async def get_orders_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    status_counts = {status: count for status, count in result.all()}
    
    total_orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = total_orders_result.scalar() or 0
    
    return {
        "total_orders": total_orders,
        "status_counts": status_counts
    }


@router.get("/reports/sellers")
async def get_sellers_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    total_sellers_result = await db.execute(select(func.count(Seller.id)))
    total_sellers = total_sellers_result.scalar() or 0
    
    active_sellers_result = await db.execute(select(func.count(Seller.id)).where(Seller.is_active == True))
    active_sellers = active_sellers_result.scalar() or 0
    
    avg_rating_result = await db.execute(select(func.avg(Seller.rating)))
    avg_rating = avg_rating_result.scalar() or 0.0
    
    return {
        "total_sellers": total_sellers,
        "active_sellers": active_sellers,
        "average_seller_rating": float(avg_rating)
    }


@router.get("/reports/customers")
async def get_customers_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    total_customers_result = await db.execute(select(func.count(Customer.id)))
    total_customers = total_customers_result.scalar() or 0
    
    active_customers_result = await db.execute(select(func.count(Customer.id)).where(Customer.is_active == True))
    active_customers = active_customers_result.scalar() or 0
    
    return {
        "total_customers": total_customers,
        "active_customers": active_customers
    }


@router.get("/reports/weekly")
async def get_weekly_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    result = await db.execute(
        select(func.date_trunc('day', Order.created_at).label('day'), func.sum(Order.total_amount).label('sales'))
        .where(Order.created_at >= seven_days_ago)
        .group_by('day')
        .order_by('day')
    )
    
    trend = [{"day": row.day.strftime('%Y-%m-%d'), "sales": float(row.sales or 0)} for row in result.all()]
    return {"weekly_sales_trend": trend}


@router.get("/reports/monthly")
async def get_monthly_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_is_admin(current_user.role_id)
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    result = await db.execute(
        select(func.date_trunc('day', Order.created_at).label('day'), func.sum(Order.total_amount).label('sales'))
        .where(Order.created_at >= thirty_days_ago)
        .group_by('day')
        .order_by('day')
    )
    
    trend = [{"day": row.day.strftime('%Y-%m-%d'), "sales": float(row.sales or 0)} for row in result.all()]
    return {"monthly_sales_trend": trend}
