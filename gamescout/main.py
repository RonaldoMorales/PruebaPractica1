from .database import create_db_and_tables
from .repository import ProductRepository
from .scraper import scrape_products


def main():
    create_db_and_tables()

    products = scrape_products()

    repository = ProductRepository()

    repository.upsert_products(products)

    top_products = repository.get_top_n(5)

    print("\nTOP 5 PRODUCTOS MÁS CAROS:")

    for product, product_type in top_products:
        print(
            f"{product.title} | "
            f"{product.price_eur}€ | "
            f"{product_type}"
        )


if __name__ == "__main__":
    main()
