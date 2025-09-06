import httpx                        # Para hacer solicitudes HTTP
from bs4 import BeautifulSoup       # Para parsear el HTML
import json                         # Para imprimir en formato JSON
import asyncio 
from app.services.metodosGenericos import ordenar_por_campo
async def fetch_data_items_ml(search: str, limit: int = 30, campo = "name" ,descendente = False):
    """
    Realiza una búsqueda en www.mottesimateriales.com.ar y extrae los productos del bloque div que contengan la siguiente clase `js-item-product`
    que contiene toda la información de cada producto.

    Args:
        search (str): Término de búsqueda.

    Returns:
        List[dict]: Lista de productos encontrados con sus datos normalizados.
    """
    # remplaza los espacios con el simbolo '+' para una busqueda más efectiva y necesario para esta pagina en particular
    search = search.lower();
    
    search_text = search.replace(" ","%20")
    
    search = search.replace(" ","-")
    
    if (search == '' or search == None):
        return []
    url = f"https://listado.mercadolibre.com.ar/construccion/materiales-obra/obra-pesada/{search}_NoIndex_True?sb=category#D[A:{search_text}]" 
    
    # Definis tus cookies necesarias
    cookies = {
        'last_query': search,
        # '_csrf': 'Z1x5THU_ZjBs1KrLAFu8UNYC',
        # '_d2id': 'fe9b98ad-29ea-470b-a686-9ceba6db7130-n',
    }
    
    # Definicion de headers
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "es-AR,es;q=0.9",
    "Referer": "https://www.mercadolibre.com.ar/",
    "Origin": "https://www.mercadolibre.com.ar/",
    "Connection": "keep-alive",
    }


    try:
        # Solicitar la página web
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, cookies=cookies)
            res.raise_for_status()

        # Parsear el HTML de la página
        soup = BeautifulSoup(res.text, "html.parser")

        # Buscar todos los elementos <div> que contienen la información del producto
        product_ol = soup.find("ol", class_="ui-search-layout")

        products = []
        for product_li in product_ol.find_all("li", class_="ui-search-layout__item")[:limit]:
            # print(product_li.find("a", class_="poly-component__title").text.strip())
            # # break
            product_data = extract_product_data(product_li)
            if product_data:
                products.append(product_data)

        return ordenar_por_campo(products, campo, descendente)

    except httpx.RequestError as e:
        print("Error de conexión:", e)
        return []

def extract_product_data(product_li):
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
            "stock": int | None,
            "brandName": str | None,
            "category": str | None,
            "discountPercentage": int | None,
        }
    """

    # Inicializar valores por defecto
    product_id = name = price_short = price_number = link = stock = brandName = discountPercentage = category = None
    default_image_url = "https://acdn-us.mitiendanube.com/stores/001/258/599/themes/common/logo-1636121110-1663682413-ff5e07835dc96cbf78797acba0239c841663682413-480-0.webp"
    image_url = default_image_url

    try: 
            
            # Acceder al campo price
            
            price_tag = product_li.find("span", class_="andes-money-amount__fraction")    
            if price_tag:
                raw_price = price_tag.text.strip().replace(".", "")
                price_number = int(raw_price)
                price_short = f"${price_number}"
        
            name_tag = product_li.find("a", class_="poly-component__title")
            if name_tag:
                name = name_tag.text.strip()

            image_tag = product_li.find("img", class_="poly-component__picture")
            if image_tag and image_tag.get("src"):
                
                image_url = image_tag.get("data-src") if image_tag.get("data-src") else image_tag.get("src")
                
            link = name_tag["href"].split(" ")[0].strip()
            
            brand_tag = product_li.find("span", class_="poly-component__seller")
            if brand_tag:
                brandName = "Mercado Libre: " + brand_tag.text.strip()

            discount_tag = product_li.find("span", class_="andes-money-amount__discount")
            discountPercentage = (
                discount_tag.text.strip().split("%")[0] if discount_tag else None
            )
        
            stock = 1
            
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
        "source":"Mercado Libre",
        "brandName": brandName,
        "category": category,
        "discountPercentage": discountPercentage,
        "logo":"https://acdn-us.mitiendanube.com/stores/001/258/599/themes/common/logo-1636121110-1663682413-ff5e07835dc96cbf78797acba0239c841663682413-480-0.webp"  
    }

def ordenar_por_campo(lista, campo, descendente=False):
    """
    Ordena una lista de objetos (dicts) por el campo especificado.
    Si el campo no existe o es None, lo pone al final.
    """
    def clave(obj):
        valor = obj.get(campo)
        if isinstance(valor, str) and valor.replace(".", "").isdigit():
            return float(valor.replace(".", ""))
        return valor if valor is not None else float('inf') if not descendente else float('-inf')

    return sorted(lista, key=clave, reverse=descendente)


# # Ejecutar como script para probar
# if __name__ == "__main__":
#     products = asyncio.run(fetch_data_items_ml("cemento pcr 2000", 15, "price_number", True)) 
#     print(json.dumps(products, indent=2, ensure_ascii=False))