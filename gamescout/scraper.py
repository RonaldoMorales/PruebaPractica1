"""Scraper de productos desde el sitio de GameScout."""
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def scrape_products() -> list[dict]:
     """Extrae productos y sus datos desde el sitio web."""
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    base_url = "https://sandbox.oxylabs.io/products"

    products_data = []

    try:
        for page in range(1, 6):
            url = f"{base_url}?page={page}"
            driver.get(url)

            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.product-card")
                )
            )

            products = driver.find_elements(
                By.CSS_SELECTOR,
                "div.product-card"
            )

            for product in products:
                try:
                    title = product.find_element(
                        By.CSS_SELECTOR,
                        "h4.title"
                    ).text

                    categoria = product.find_element(
                        By.CSS_SELECTOR,
                        "p.category"
                    ).text

                    categoria = " ".join(
                        categoria.split()[1:]
                    )

                    precio = product.find_element(
                        By.CSS_SELECTOR,
                        "div.price-wrapper"
                    ).text

                    precio = precio.replace(
                        "€",
                        ""
                    ).replace(
                        ",",
                        "."
                    ).strip()

                    precio = float(precio)

                    product_id = product.find_element(
                        By.CSS_SELECTOR,
                        "a"
                    ).get_attribute(
                        "href"
                    ).split("/")[-1]

                    product_data = {
                        "product_id": int(product_id),
                        "title": title,
                        "type": categoria,
                        "price_eur": precio,
                        "scraped_at": datetime.now(),
                    }

                    products_data.append(product_data)

                except Exception as e:
                    print(
                        f"Error al procesar el producto: {e}"
                    )

                    continue

    finally:
        driver.quit()

    return products_data