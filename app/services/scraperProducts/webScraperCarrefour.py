from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import time
import asyncio, json


async def fetch_data_layer_items(search: str, limit: int = 20):
    """
    Busca productos en easy.com.ar usando Playwright para renderizar JavaScript
    y obtiene los datos tanto del HTML como del dataLayer.
    """
    # remplaza los espacios con el simbolo '%20' para una busqueda más efectiva y necesario para esta pagina en particular

    if (
        len(search) < 3
    ):  # esto previene busquedas innecesarias para palabras menores de 3
        return []
    search = search.replace(" ", "%20")
    
    # Construye la URL de búsqueda con parámetros específicos para Easy
    url = f"https://www.carrefour.com.ar/{search}t?_q={search}t"
    start_time = time.time()  # <--- inicio del timer
    # Inicia Playwright en modo asincrónico
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # Sin interfaz gráfica
            page = await browser.new_page()

            # Navega a la URL y espera que la red esté inactiva (carga completa)
            await page.goto(url, timeout=10000)

            html = await page.content()
            # data_layer = await page.evaluate("window.dataLayer")

            # Cierra el navegador para liberar recursos
            await browser.close()
        except Exception as e:

            raise RuntimeError(f"No se encontró el contenedor de productos: {e}")
            # return []

    # Parsea el HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Busca el contenedor principal de productos
    product_divs = soup.find(
        "div", class_="valtech-carrefourar-search-result-3-x-gallery"
    )
    # print(product_divs)

    if not product_divs:
        return []

    products_div = product_divs.find_all(
        "div", class_="valtech-carrefourar-search-result-3-x-galleryItem"
    )

    products = []
    end_time = time.time()  # <--- fin del timer
    print(
        f"[Servidor - consulta a carrefour] Tiempo de respuesta de la peticion: {end_time - start_time:.2f} segundos"
    )  # <--- solo para logs

    # limite de respuesta
    products_div = products_div[:limit]

    for product_div in products_div:
        product_data = extract_product_data(product_div)
        if product_data:
            products.append(product_data)

    return products


def extract_product_data(product_div):
    """
    Extrae la información relevante de un producto desde el contenedor HTML de Carrefour.

    Args:
    product_div : bs4.element.Tag
        Contenedor HTML del producto.

    Returns:
    dict
        Diccionario con los datos del producto.
    """
    try:
        start_time = time.time()  # <--- inicio del timer
        # Nombre del producto
        name_tag = product_div.find(
            "span", class_="vtex-product-summary-2-x-productBrand"
        )
        name = name_tag.text.strip() if name_tag else None

        # Precio reconstruido desde múltiples spans
        price_container = product_div.find(
            "div", class_="vtex-flex-layout-0-x-flexColChild--wrapPrice"
        )
        price_number = None
        if price_container:
            currency_integers = price_container.find_all(
                "span", class_="valtech-carrefourar-product-price-0-x-currencyInteger"
            )
            currency_group = price_container.find(
                "span", class_="valtech-carrefourar-product-price-0-x-currencyGroup"
            )
            currency_fraction = price_container.find(
                "span", class_="valtech-carrefourar-product-price-0-x-currencyFraction"
            )

            if currency_integers and currency_group and currency_fraction:
                integer_part = "".join(
                    [span.text.strip() for span in currency_integers]
                )
                decimal_part = currency_fraction.text.strip()
                raw_price = f"{integer_part}.{decimal_part}"
                try:
                    price_number = float(raw_price.replace(",", ""))
                except ValueError:
                    price_number = None

        # Imagen del producto
        image_tag = product_div.find("img")
        image_url = (
            image_tag.get("src")
            if image_tag and image_tag.get("src")
            else "https://carrefour.com.ar/default-image.svg"
        )

        # Link al producto
        link_tag = product_div.find("a", href=True)
        link = f"https://www.carrefour.com.ar{link_tag['href']}" if link_tag else None

        # Marca (si está disponible)
        brand_tag = product_div.find(
            "span", class_="vtex-product-summary-2-x-brandName"
        )
        brandName = brand_tag.text.strip() if brand_tag else None

        return {
            "id": None,
            "image": image_url,
            "link": link,
            "name": name,
            "price": price_number,
            "source": "Carrefour",
            "unit": "unidad",
            "unitPrice": price_number,
            "brandName": brandName,
        }

    except Exception as e:
        print("Error al extraer producto:", e)
        return None


# products = asyncio.run(fetch_data_layer_items("fernet branca"))
# print(json.dumps(products, indent=2, ensure_ascii=False))
