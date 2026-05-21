from .base import *


class StockHistory(Base):
    __tablename__ = "stock_history"

    id = Column(Integer, primary_key=True, index=True)

    quantity_changed = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)
    reference_id = Column(Integer, nullable=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="stock_history")
