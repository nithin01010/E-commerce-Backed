from .base import * 

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    quantity = Column(Integer, nullable=False)
    status = Column(String(255), default="Order placed",nullable=False)
    total_amount = Column(Integer, nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    address = relationship("Address", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    seller = relationship("Seller", back_populates="orders")
    returns = relationship("Return", back_populates="order")
    reviews = relationship("Review", back_populates="order")