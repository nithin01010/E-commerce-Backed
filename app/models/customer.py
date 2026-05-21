from .base import *


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    user = relationship("User", back_populates="customers")
    address = relationship("Address", back_populates="customers")
    orders = relationship("Order", back_populates="customers")
    cart = relationship("Cart", back_populates="customers")
    reviews = relationship("Review", back_populates="customers")