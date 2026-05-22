from .base import *


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, index=True, nullable=False)



    address = relationship("Address", back_populates="customers")

