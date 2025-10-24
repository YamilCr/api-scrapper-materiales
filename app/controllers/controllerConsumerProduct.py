from app.services.scraperProducts.webScraperCarrefour import (
    fetch_data_layer_items as fetch_carrefour,
)
from app.services.scraperProducts.webScraperLaAnonima import (
    fetch_products_la_anonima as fetch_laanonima,
)
from app.services.scraperProducts.webScraperMasOnline import (
    fetch_data_layer_items as fetch_masOnline,
)
import asyncio
import logging

logger = logging.getLogger(__name__)
# Diccionario de funciones por proveedor
PROVEEDORES = {
    "carrefour": fetch_carrefour,
    "laanonima": fetch_laanonima,
    "masonline": fetch_masOnline,
}


def fetch_all_products(search: str, limit: int = 50):
    async def safe_call(coro, timeout=15):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except Exception as e:
            logger.warning(f"[fetch_all_products] Error en {coro.__name__}: {e}")
            return []

    async def gather_all():
        tasks = [
            safe_call(fetch_laanonima(search, 7), timeout=15),
            safe_call(fetch_carrefour(search, 7), timeout=12),
            safe_call(fetch_masOnline(search, 7), timeout=10),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=False)
        all_items = [
            item for sublist in results for item in sublist if isinstance(sublist, list)
        ]
        return all_items[:limit]

    return asyncio.run(gather_all())


# funcion para la busqueda por proveedor en especifico
def fetch_products_proveedor(proveedor: str, search: str, limit: int = 20):

    # esto devuelve el metodo scrapper de cada proveedor
    scraper = PROVEEDORES.get(proveedor)
    if not scraper:
        raise RuntimeError(f"Proveedor '{proveedor.lower()}' no soportado")

    # esto es para comprobar si es un metodo async o sync del scraper
    if asyncio.iscoroutinefunction(scraper):
        # realiza la busqueda en el proveedor en especifico
        return asyncio.run(scraper(search, limit))
    else:
        return scraper(search, limit)
