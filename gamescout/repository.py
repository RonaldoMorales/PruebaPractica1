"""Repositorio para gestionar productos y tipos de productos."""

from typing import Iterable

from sqlmodel import Session, select

from .database import get_engine
from .models import Product, ProductType


class ProductRepository:
     """Gestiona las operaciones de persistencia de productos."""
    def __init__(self):
        self.engine = get_engine()

    def get_or_create_type(
        self,
        name: str,
        session: Session
    ) -> ProductType:
        product_type = session.exec(
            select(ProductType).where(
                ProductType.name == name
            )
        ).first()

        if product_type is not None:
            return product_type

        product_type = ProductType(name=name)

        session.add(product_type)
        session.flush()

        return product_type

    def upsert_products(
        self,
        products: Iterable[dict]
    ) -> None:
        with Session(self.engine) as session:
            for product_data in products:
                product_type = self.get_or_create_type(
                    product_data["type"],
                    session
                )

                product = session.exec(
                    select(Product).where(
                        Product.product_id
                        == product_data["product_id"]
                    )
                ).first()

                if product is None:
                    product = Product(
                        product_id=product_data["product_id"],
                        title=product_data["title"],
                        price_eur=product_data["price_eur"],
                        scraped_at=product_data["scraped_at"],
                        type_id=product_type.id,
                    )

                    session.add(product)

                else:
                    product.title = product_data["title"]
                    product.price_eur = product_data["price_eur"]
                    product.scraped_at = product_data["scraped_at"]
                    product.type_id = product_type.id

            session.commit()

    def get_top_n(
        self,
        n: int
    ) -> list[tuple[Product, str]]:
        with Session(self.engine) as session:
            products = session.exec(
                select(Product)
                .order_by(Product.price_eur.desc())
                .limit(n)
            ).all()

            return [
                (product, product.type.name)
                for product in products
            ]

    def get_products_by_type(
        self,
        type_name: str
    ) -> list[Product]:
        with Session(self.engine) as session:
            product_type = session.exec(
                select(ProductType).where(
                    ProductType.name == type_name
                )
            ).first()

            if product_type is None:
                return []

            return product_type.products