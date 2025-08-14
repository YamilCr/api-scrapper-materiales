import httpx                        # Para hacer solicitudes HTTP
from bs4 import BeautifulSoup       # Para parsear el HTML
import json                         # Para imprimir en formato JSON
import asyncio

async def fetch_data_items_neomat(search: str, limit: int = 15):
    """
    Realiza una búsqueda en neomat.com.ar y extrae los productos del bloque div que contengan la siguiente clase `js-item-product`
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
    
    url = f"https://neomat.com.ar/search/?q={search}"
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
        product_divs = soup.find_all("div", class_="js-item-product")
        # product_divs[0]
        products = []
        for product_div in product_divs[:limit]:
            # print(product_div)
            
            product_data = extract_product_data(product_div)
            if product_data:
                products.append(product_data)

        return products

    except httpx.RequestError as e:
        print("Error de conexión:", e)
        return []

def extract_product_data(product_div):
    """
    Extrae la información relevante de un producto desde un contenedor HTML.

    Args:
    product_div : bs4.element.Tag
        Contenedor HTML del producto (debe ser un <div> que contenga los elementos esperados).

    Returns:
    dict
        Un diccionario con la siguiente estructura:
        {
            "product_id": str | None,
            "name": str | None,
            "price_short": str | None,
            "price_number": float | None,
            "image_url": str,
            "link": str | None,
            "stock": int | None,
            "brandName": str | None,
            "category": str | None,
            "discountPercentage": int | None,
        }
    """

    # Inicializar valores por defecto
    product_id = name = price_short = price_number = link = stock = brandName = discountPercentage = category = None
    default_image_url = "https://acdn-us.mitiendanube.com/stores/002/199/725/themes/common/logo-882666800-1659546188-17c7b31dcb7291c808ccb2d33fd16e0b1659546188-480-0.png?0"
    image_url = default_image_url


    try:
        script_tag = product_div.find('script', {'type': 'application/ld+json', 'data-component': 'structured-data.item'})
        
        variant_container = product_div.find("div", class_="js-product-container")
        data_variants_raw = variant_container.get("data-variants")

        if data_variants_raw and script_tag:
            # Cargar el contenido como JSON
            data = json.loads(script_tag.string)
            variants = json.loads(data_variants_raw)
            variant = variants[0]  # Suponemos que el primer elemento contiene los datos relevantes
            
            # Acceder al campo
            brandName = data.get('brand', {}).get('name', 'Marca no encontrada')
            product_id = variant.get("product_id")
            price_short = variant.get("price_short")
            price_number = variant.get("price_number")
            stock = variant.get("stock")

            name_tag = product_div.find("div", class_="js-item-name")
            if name_tag:
                name = name_tag.text.strip()

            image_tag = product_div.find("img", class_="js-product-item-image-private")
            if image_tag and image_tag.get("data-srcset"):
                image_url = image_tag["data-srcset"].split(" ")[0].strip()

            link_tag = product_div.find("a", class_="js-product-item-image-link-private")
            if link_tag:
                link = link_tag.get("href")

    except (json.JSONDecodeError, IndexError, KeyError, AttributeError) as e:
        print("Error encontrado: ", e )
        return {}

    return {
        "product_id": product_id,
        "name": name,
        "price_short": price_short,
        "price_number": price_number,
        "image_url": image_url,
        "link": link,
        "stock": stock,
        "source":"NeoMat",
        "brandName": brandName,
        "category": category,
        "discountPercentage": discountPercentage,
        "logo":"https://acdn-us.mitiendanube.com/stores/002/199/725/themes/common/logo-882666800-1659546188-17c7b31dcb7291c808ccb2d33fd16e0b1659546188-480-0.png?0"
    }


# Ejecutar como script para probar
# if __name__ == "__main__":
#     products = asyncio.run(fetch_data_items_neomat("cemento PCR 2000"))
#     print(json.dumps(products, indent=2, ensure_ascii=False))