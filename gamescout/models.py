"""Modelos de datos de GameScout."""

from datetime import datetime
from typing import List, Optional

from sqlmodel import (
    Column,
    DateTime,
    Field,
    Float,
    Relationship,
    SQLModel,
    String,
)


class ProductType(SQLModel, table=True):
    """Representa el tipo o categoría de un producto."""

    id: int = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        sa_column=Column(
            String,
            nullable=False,
            unique=True
        )
    )

    products: List["Product"] = Relationship(
        back_populates="type"
    )


class Product(SQLModel, table=True):
    """Representa un producto obtenido mediante scraping."""

    id: int = Field(
        default=None,
        primary_key=True
    )

    product_id: int = Field(
        unique=True,
        index=True,
        nullable=False,
        ge=1
    )

    title: str = Field(
        sa_column=Column(
            String,
            nullable=False
        )
    )

    price_eur: float = Field(
        ge=0,
        sa_column=Column(
            Float,
            nullable=False
        )
    )

    scraped_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False
        )
    )

    type_id: int = Field(
        foreign_key="producttype.id"
    )

    type: Optional[ProductType] = Relationship(
        back_populates="products"
    )
