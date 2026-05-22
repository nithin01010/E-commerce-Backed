from .base import *


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    street = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    country = Column(String(100), default="India", nullable=False)
    is_default = Column(Boolean, default=False)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=True)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="addresses")
    seller = relationship("Seller", back_populates="addresses")
    orders = relationship("Order", back_populates="address")