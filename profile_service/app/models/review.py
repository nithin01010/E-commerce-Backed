from .base import * 


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order = relationship("Order", back_populates="reviews")