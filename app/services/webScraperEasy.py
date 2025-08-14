from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
# from playwright.sync_api import sync_playwright
from itertools import zip_longest

  
async def fetch_data_layer_items(search: str, limit: int = 20):
    """
    Busca productos en easy.com.ar usando Playwright para renderizar JavaScript
    y obtiene los datos tanto del HTML como del dataLayer.
    """
    # remplaza los espacios con el simbolo '%20' para una busqueda más efectiva y necesario para esta pagina en particular
    
    if (len(search) < 3): # esto previene busquedas innecesarias para palabras menores de 3
        return []
    search = search.replace(" ","%20")
    
    # Construye la URL de búsqueda con parámetros específicos para Easy
    url = f"https://www.easy.com.ar/{search}?_q={search}&map=ft"

    # Inicia Playwright en modo asincrónico
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)  # Sin interfaz gráfica
            page = await browser.new_page()

            # Navega a la URL y espera que la red esté inactiva (carga completa)
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Espera explícita a que aparezca el contenedor de productos
            await page.wait_for_selector("#gallery-layout-container", timeout=10000)

            # Captura el HTML renderizado y el objeto JavaScript `dataLayer`
            html = await page.content()
            data_layer = await page.evaluate("window.dataLayer")

            # Cierra el navegador para liberar recursos
            await browser.close()
        except Exception as e:
        
            # return []
            raise RuntimeError(f"No se encontró el contenedor de productos: {e}")


    # Parsea el HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Busca el contenedor principal de productos
    product_divs = soup.find("div", id="gallery-layout-container")
    
    if not product_divs:
        return []

    # Buscar el primer bloque con ecommerce.impressions
    list_products = []
    for entry in data_layer:
        ecommerce = entry.get("ecommerce")
        if ecommerce and "impressions" in ecommerce:
            list_products = ecommerce["impressions"]
            break
    
    if not list_products:
        return []

    products_div = product_divs.find_all(
        "div",
        class_="arcencohogareasy-cmedia-integration-cencosud-1-x-galleryItem"
    )

    products = []
    # limite de respuesta
    products_div = products_div[:limit]
    list_products = list_products[:limit]

    for product_div, product_js in zip_longest(products_div, list_products):
        # print(product_div)
        # break
        product_data = extract_product_data(product_div, product_js)
        if product_data:
            products.append(product_data)

    return products

def extract_product_data(product_div, product_js):
    """Extrae y fusiona datos de un producto desde el HTML y el dataLayer."""
    
     # Inicializar valores por defecto
    product_id = name = price_short = price_number = link = stock = brandName = discountPercentage = category = None    
    default_image_url = "https://arcencohogareasy.vtexassets.com/assets/vtex.file-manager-graphql/images/e3cfab5b-2965-44d0-9c58-c3f3ca4b2bac___73d2acbdf5bcfbbcf7de22ba69d9163e.svg"

    try:
        
        # verifico si hay datos en product_js para prevenir errores
        if product_js:
            
            product_id = product_js.get("id")
            category = product_js.get("category")
            name_js = product_js.get("name")
            brand_js = product_js.get("brand")
            price_number = product_js.get("price")

        # Nombre del producto (HTML > JS)
        name_tag = product_div.find("h2")
        name_html = name_tag.text.strip() if name_tag else None
        name = name_html or name_js

        # Imagen
        image_tag = product_div.find("img", class_="vtex-product-summary-2-x-imageNormal")
        image_url = image_tag["src"] if image_tag and image_tag.get("src") else default_image_url

        # Marca (HTML > JS)
        brand_tag = product_div.find("span", class_="vtex-product-summary-2-x-productBrandName")
        brand_html = brand_tag.text.strip() if brand_tag else None
        brandName = brand_html or brand_js

        # Precio corto (HTML)
        price_short_tag = (
            product_div.find("div", class_="sellingPriceDivSearch")
            if product_div.find("div", class_="containerPriceM2Search") is None
            else product_div.find("div", class_="containerPriceM2Search")
        )
        price_short = price_short_tag.text.strip() if price_short_tag else None

        # Precio numérico (JS > HTML parseado)
        if not price_number and price_short:
            try:
                price_number = float(price_short.replace("$", "").replace(".", "").replace(",", "."))
            except:
                price_number = None


        # Link
        link_tag = product_div.find("a", class_="vtex-product-summary-2-x-clearLink")
        link = f"https://www.easy.com.ar{link_tag.get('href')}" if link_tag and link_tag.get("href") else "#"

        # Descuento
        discount_tag = product_div.find("span", class_="vtex-product-price-1-x-savingsPercentage")
        discountPercentage = (
            discount_tag.text.strip().replace("%", "") if discount_tag else None
        )

        # Stock (por defecto 1 si aparece en la galería)
        stock = 1

        return {
            "product_id": product_id,
            "name": name,
            "price_short": price_short,
            "price_number": price_number,
            "image_url": image_url,
            "link": link,
            "stock": stock,
            "source": "Easy",
            "brandName": brandName,
            "category": category,
            "discountPercentage": discountPercentage,
            "logo": default_image_url
        }

    except Exception as e:
        print("Error procesando producto:", e)
        return {}
