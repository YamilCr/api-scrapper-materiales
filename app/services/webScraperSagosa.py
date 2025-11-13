import httpx                        # Para hacer solicitudes HTTP
from bs4 import BeautifulSoup       # Para parsear el HTML
import json                         # Para imprimir en formato JSON
from app.services.decorator import with_timeout_and_log
import asyncio, json, time

@with_timeout_and_log(timeout=20)
async def fetch_data_items_sagosa(search: str, limit: int = 15):
    """
    Realiza una búsqueda en www.mottesimateriales.com.ar y extrae los productos del bloque div que contengan la siguiente clase `js-item-product`
    que contiene toda la información de cada producto.

    Args:
        search (str): Término de búsqueda.

    Returns:
        List[dict]: Lista de productos encontrados con sus datos normalizados.
    """
    # remplaza los espacios con el simbolo '+' para una busqueda más efectiva y necesario para esta pagina en particular
    search = search.replace(" ","+")
    
    if (search == '' or search == None):
        return []
    url = f"https://www.sagosa.com.ar/busqueda?controller=search&s={search}"
    start_time = time.time()  # <--- inicio del timer
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        # Solicitar la página web
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
            res.raise_for_status()

        # Parsear el HTML de la página
        soup = BeautifulSoup(res.text, "html.parser")

        # Buscar todos los elementos <div> que contienen la información del producto
        product_divs = soup.find_all("article", class_="product-miniature")

        products = []
        end_time = time.time()  # <--- fin del timer
        print(
            f"[Servidor - Sagosa] Tiempo de respuesta de la peticion: {end_time - start_time:.2f} segundos"
        )  # <--- solo para logs

        for product_div in product_divs[:limit]:
            # print(product_div)
            # break
            product_data = extract_product_data(product_div)
            if product_data:
                products.append(product_data)

        return products

    except httpx.RequestError as e:
        print("Error de conexión:", e)
        return []

import json

def extract_product_data(product_div):
    """
    Extrae la información relevante de un producto desde un contenedor HTML <article>.
    """

    # Valores por defecto
    product_id = name = price_short = price_number = link = stock = brandName = discountPercentage = category = None
    default_image_url = "https://acdn-us.mitiendanube.com/stores/001/258/599/themes/common/logo-1636121110-1663682413-ff5e07835dc96cbf78797acba0239c841663682413-480-0.webp"
    image_url = default_image_url

    try:
        # ID del producto
        product_id = product_div.get("data-id-product")

        # Nombre
        name_tag = product_div.find("h3", class_="product-title")
        if name_tag and name_tag.a:
            name = name_tag.a.text.strip()
            link = name_tag.a.get("href")

        # Marca
        brand_tag = product_div.find("div", itemprop="brand")
        if brand_tag:
            brandName = brand_tag.find("meta", itemprop="name").get("content")

        # Precio
        price_tag = product_div.find("span", class_="price")
        if price_tag:
            price_short = price_tag.text.strip()
            try:
                price_number = float(price_tag.get("content"))
            except (ValueError, TypeError):
                price_number = None

        # Imagen principal
        img_tag = product_div.find("meta", itemprop="image")
        if img_tag:
            image_url = img_tag.get("content")

        # Stock
        availability_tag = product_div.find("link", itemprop="availability")
        if availability_tag and "InStock" in availability_tag.get("href", ""):
            stock = 1
        else:
            stock = 0

    except Exception as e:
        print("Error encontrado:", e)

    return {
        "product_id": product_id,
        "name": name,
        "price_short": price_short,
        "price_number": price_number,
        "image_url": image_url,
        "link": link,
        "stock": stock,
        "source": "Sagosa",
        "brandName": brandName,
        "category": category,
        "discountPercentage": discountPercentage,
        "logo": default_image_url
    }

# # Ejecutar como script para probar
# if __name__ == "__main__":
#     products = asyncio.run(fetch_data_items_sagosa("cal")) 
#     print(json.dumps(products, indent=2, ensure_ascii=False))