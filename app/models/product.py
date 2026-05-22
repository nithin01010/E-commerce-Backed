from .base import *


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    is_verified = Column(Boolean, default=False, nullable=False)
    status = Column(String(255), default="under verfication", nullable=False)
    rating = Column(Float, nullable=True)
    search_vector = Column(TSVECTOR, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    seller = relationship("Seller", back_populates="products")
    category = relationship("Category", back_populates="products")
    stock_history = relationship("StockHistory", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product")
    cart_items = relationship("Cart", back_populates="product")

class ProductImage(Base):
    __tablename__ = "productimages"

    id = Column(Integer, primary_key=True, index=True)

    url = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product", back_populates="images")