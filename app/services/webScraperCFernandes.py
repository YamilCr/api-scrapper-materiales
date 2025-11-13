import httpx                        # Para hacer solicitudes HTTP
from bs4 import BeautifulSoup       # Para parsear el HTML
import json                         # Para imprimir en formato JSON
from app.services.decorator import with_timeout_and_log
import asyncio, json, time

@with_timeout_and_log(timeout=20)
async def fetch_data_items(search: str, limit: int = 15):
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
    url = f"https://www.corralon-fernandes.com/module/iqitsearch/searchiqit?s={search}"
    start_time = time.time()  # <--- inicio del timer
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Referer": "https://www.corralon-fernandes.com/"
    }


    try:
        # Solicitar la página web
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
            res.raise_for_status()

        # Parsear el HTML de la página
        soup = BeautifulSoup(res.text, "html.parser")

        # Buscar todos los elementos <div> que contienen la información del producto
        product_divs = soup.find_all("div", class_="js-product-miniature-wrapper")
        # print(product_divs)
        # return []
        products = []
        end_time = time.time()  # <--- fin del timer
        print(
            f"[Servidor - Corralòn fernandes] Tiempo de respuesta de la peticion: {end_time - start_time:.2f} segundos"
        )  # <--- solo para logs
        # print(f"Productos encontrados: {len(product_divs)}")
        for product_div in product_divs[:limit]:
            # print(product_div)
            # break
            product_data = extract_product_data(product_div)
            if product_data:
                products.append(product_data)

        return products

    except httpx.RequestError as e:
        print(f"Error de conexión: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP: {e.response.status_code} - {e.response.text[:200]}")

def extract_product_data(product_div):
    product_id = product_div.get("data-id-product")
    name = category = brandName = reference = price_short = link = None
    price_number = stock = None
    image_url = "https://www.corralon-fernandes.com/img/logo.png"

    try:
        # ID del producto desde input
        hidden_input = product_div.find("input", {"name": "id_product"})
        if hidden_input:
            product_id = hidden_input.get("value")
        # Nombre y link
        title_tag = product_div.find("h2", class_="product-title")
        if title_tag and title_tag.a:
            name = title_tag.a.text.strip()
            link = title_tag.a.get("href")

        # Categoría
        category_tag = product_div.find("div", class_="product-category-name")
        if category_tag:
            category = category_tag.text.strip()

        # Marca
        brand_tag = product_div.find("div", class_="product-brand")
        if brand_tag and brand_tag.a:
            brandName = brand_tag.a.text.strip()

        # Referencia
        ref_tag = product_div.find("div", class_="product-reference")
        if ref_tag and ref_tag.a:
            reference = ref_tag.a.text.strip()

        # Precio
        price_tag = product_div.find("span", class_="product-price")
        if price_tag:
            price_short = price_tag.text.strip()
            import re
            clean_price = re.sub(r"[^\d,\.]", "", price_short)
            clean_price = clean_price.replace(".", "").replace(",", ".")
            try:
                price_number = float(clean_price)
            except ValueError:
                price_number = None

        # Imagen
        img_tag = product_div.find("img")
        if img_tag and img_tag.get("data-src"):
            image_url = img_tag.get("data-src")

        # Stock (no está explícito)
        stock = 1

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
        "source": "Corralón Fernandes",
        "brandName": brandName,
        "category": category,
        "reference": reference,
        "discountPercentage": None,
        "logo": "https://www.corralon-fernandes.com/img/logo.png"
    }

# Ejecutar como script para probar
if __name__ == "__main__":
    products = asyncio.run(fetch_data_items("cemento")) 
    print(json.dumps(products, indent=2, ensure_ascii=False))