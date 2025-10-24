import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

async def fetch_products_la_anonima(search: str, limit: int = 20):
    """
    Busca productos en La Anónima simulando scroll y devolviendo
    los datos en el mismo formato que MásOnline.
    """
    if len(search) < 3:
        return []

    url = f"https://www.laanonima.com.ar/buscar/{search.replace(' ', '%20')}"

    cookies = [
        {"name": "ciudad", "value": "Neuquén", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "ciudad_id", "value": "1568", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "codigoPostal", "value": "9000", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "descripcionLocalidadCabezal", "value": "Comodoro Rivadavia", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "Id-Sucursal-Electro", "value": "190", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "Id-Sucursal-Super", "value": "47", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "idZonaPrecio", "value": "8", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "operadorLogistico", "value": "AND", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "provincia", "value": "Neuquén", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "provincia_id", "value": "16", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "tipoEnvioUnificado", "value": "3", "domain": ".laanonima.com.ar", "path": "/"},
        {"name": "PHPSESSID", "value": "df8d92dab9e0dd0c3cdad5a40707eb2b", "domain": "api.laanonima.com.ar", "path": "/"},
        {"name": "s_laanonima", "value": "df8d92dab9e0dd0c3cdad5a40707eb2b", "domain": ".api.laanonima.com.ar", "path": "/"},
    ]
    
    # Scroll automático solo hasta obtener 'limit' productos
    products_loaded = 0
    start_time = time.time()  # <--- inicio del timer

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        await context.add_cookies(cookies)
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Scroll automático para cargar productos dinámicos
        last_height = await page.evaluate("document.body.scrollHeight")
        while products_loaded < limit:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)  # esperar a que cargue
                product_divs = await page.query_selector_all("div.producto-item")
                products_loaded = len(product_divs)

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:  # no se cargó nada nuevo
                    break
                last_height = new_height

        await page.wait_for_selector("div.producto-item", timeout=60000)
        html = await page.content()
        await browser.close()

    # Parsear HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    product_divs = soup.select("div.producto-item")
    products = []
    end_time = time.time()  # <--- fin del timer
    print(f"[Servidor - consulta a la anonima online] Tiempo de respuesta de la peticion: {end_time - start_time:.2f} segundos")  # <--- solo para logs

    for div in product_divs[:limit]:
        title_tag = div.select_one(".titulo")
        price_tag = div.select_one(".precio span")
        img_tag = div.select_one("img")
        link_tag = div.select_one("a[href]")

        # Extraer datos
        name = title_tag.get_text(strip=True) if title_tag else None
        price_text = price_tag.get_text(strip=True).replace("$", "").replace(".", "").replace(",", ".") if price_tag else None
        try:
            price = float(price_text) if price_text else None
        except ValueError:
            price = None
        # print(img_tag)
        image_url = img_tag.get("data-src", "")
        link = f"https://www.laanonima.com.ar{link_tag['href']}" if link_tag else None
        codigo = div.get("id-codigo-producto")

        products.append({
            "id": codigo,
            "image": image_url,
            "link": link,
            "name": name,
            "price": price,
            "source": "La Anónima",
            "unit": "unidad",
            "unitPrice": price,
            "brandName": None  # La página no muestra marca directamente
        })

    return products


# if __name__ == "__main__":
#     data = asyncio.run(fetch_products_la_anonima("arroz", limit=5))
#     import json
#     print(json.dumps(data, indent=2, ensure_ascii=False))