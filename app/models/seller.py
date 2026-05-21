from .base import *


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(255), nullable=True)
    rating = Column(Float, nullable=True)
    earnings = Column(Numeric(12, 2), default=0.00, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="seller")
    orders = relationship("Order", back_populates="seller")
    products = relationship("Product", back_populates="seller")
