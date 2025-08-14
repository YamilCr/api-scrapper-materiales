from bs4 import BeautifulSoup
import httpx
import json
import re
import asyncio # para consultas en paralelo aun no esta en marcha

async def fetch_data_items_forte(search: str, limit: int = 15):
    """
    Realiza una búsqueda en www.forteindustrial.com.ar y extrae los productos del bloque div que contengan la siguiente clase `js-item-product`
    que contiene toda la información de cada producto.

    Args:
        search (str): Término de búsqueda.

    Returns:
        List[dict]: Lista de productos encontrados con sus datos normalizados.
    """
    # ejemplo de una url de busqueda completa de la pagina
    # https://www.forteindustrial.com.ar/search/?q=cemento&manufacturer=CASABLANCA&vv_use=Exterior&vv_color=Cemento&vv_superficial=Mate&vv_material=Acr%C3%ADlico&type=configurable~simple
    # remplaza los espacios con el simbolo '%20' para una busqueda más efectiva y necesario para esta pagina en particular
    search = search.replace(" ","%20")
    
    if (search == '' or search == None):
        return []
    url = f"https://www.forteindustrial.com.ar/search/?q={search}"
        
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
        products_ol = soup.find("ol", class_="products")
        
        if not products_ol:
            return []
        
        script = soup.find('script', string=re.compile(r'ga4DataLayer'))
        # print(script)
        if not script:
            print("No se encontró ningún <script> con 'ga4DataLayer'.")
            return []

        # Buscar contenido de ga4DataLayer({...});
        raw_json = script.string.strip()
        # print(raw_json)
        # # Parsear el JSON
        parsed = json.loads(raw_json)
        # # Navegar hasta ga4DataLayer → data
        ga4_data = parsed.get("*", {}).get("ga4DataLayer", {}).get("data", [])
        list_products = ga4_data[0]["ecommerce"]["items"]
        # print(list_products)        
        products = []
        products_ol = products_ol.find_all("li", class_="product-item")
        # limite de respuesta
        products_ol = products_ol[:limit]
        list_products = list_products[:limit]
        
        for product_li, product_js in zip(products_ol, list_products):
            # print(product_js)
            # break
            product_data = extract_product_data(product_li, product_js)
            if product_data:
                products.append(product_data)

        return products

    except httpx.RequestError as e:
        print("Error de conexión:", e)
        return []

def extract_product_data(product_li, product_js):
    """
    Extrae la información relevante de un producto desde un contenedor HTML.

    Args:
    product_li : bs4.element.Tag
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
            "stock": int | None
        }
    """

    # Inicializar valores por defecto
    product_id = name = price_short = price_number = link = stock = brandName = discountPercentage = category = None
    default_image_url = "https://media.xcons.com.ar/media/logo/stores/137/new-logo-desktop.webp"
    image_url = default_image_url
    try:
        product_id = product_js.get("item_id")
        price_short = product_js.get("price")
        price_number = product_js.get("price")
        brandName = product_id.split('-')[0] # divide la cadena de texto en una lista, utilizando el guión '-' y almaceno el primer elemento que es la marca
        category = product_js.get("item_category_3")
        stock = 1
        name = product_js.get("item_name") 
        image_tag = product_li.find("img", class_="product-image-photo")
        image_url = image_tag["srcset"].split(" ")[0].strip() if image_tag and image_tag.get("srcset") else None
        
        link_tag = product_li.find("a", href=True)
        link = link_tag["href"] if link_tag else None      

    except (json.JSONDecodeError, IndexError, KeyError, AttributeError) as e:
        print("Error encontrado: ", e )
        pass

    return {
        "product_id": product_id,
        "name": name,
        "price_short": price_short,
        "price_number": price_number,
        "image_url": image_url,
        "link": link,
        "stock": stock,
        "source":"Forte",
        "brandName": brandName,
        "category": category,
        "discountPercentage": discountPercentage,
        "logo":"https://media.xcons.com.ar/media/logo/stores/137/new-logo-desktop.webp"  
    
    }
    
# Ejecutar como script para probar
# if __name__ == "__main__":
#     products = asyncio.run(fetch_data_items_forte("cemento"))
#     print(json.dumps(products, indent=2, ensure_ascii=False))
