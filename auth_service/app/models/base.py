from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, Numeric, DateTime,
    ForeignKey, Enum, func, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import TSVECTOR