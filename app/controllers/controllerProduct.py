from app.services.webScraperEasy import fetch_data_layer_items
from app.services.webScraperMontessi import fetch_data_items_montessi
from app.services.webScraperForte import fetch_data_items_forte
from app.services.webScraperNeoMat import fetch_data_items_neomat
from app.services.webScraperML import fetch_data_items_ml
from app.services.webScraperSagosa import fetch_data_items_sagosa
from app.services.webScraperCFernandes import (
    fetch_data_items as fetch_data_items_cfernandes,
)
from app.services.webScraperParren import fetch_data_items as fetch_data_items_parren
import asyncio

# Diccionario de funciones por proveedor
PROVEEDORES = {
    # "easy": fetch_data_layer_items,
    "montessi": fetch_data_items_montessi,
    "forte": fetch_data_items_forte,
    "neomat": fetch_data_items_neomat,
    # "meli": fetch_data_items_ml,
    "sagosa": fetch_data_items_sagosa,
    "cfernandes": fetch_data_items_cfernandes,
    "perren": fetch_data_items_parren,
}

# Mapeo de ciudades a proveedores disponibles
CIUDAD_PROVEEDORES = {
    "comodoro": ["montessi", "forte", "neomat", "sagosa"],
    "trelew": ["sagosa", "cfernandes", "perren"],
}


def fetch_all_products(search: str, limit: int = 50):
    search = search.lower()

    async def gather_all():
        tasks = []
        sync_results = []

        # Iterar sobre todos los proveedores
        for proveedor, scraper in PROVEEDORES.items():
            if asyncio.iscoroutinefunction(scraper):
                # async → agregar a tasks
                tasks.append(scraper(search, 7))
            else:
                # sync → ejecutar directamente
                try:
                    sync_results.append(scraper(search, 7))
                except Exception as e:
                    print(f"Error en scraper {proveedor}: {e}")

        # Ejecutar async en paralelo
        async_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten y filtrar
        all_items = []
        for sublist in async_results + sync_results:
            if isinstance(sublist, list):
                all_items.extend(sublist)

        return all_items[:limit]

    return asyncio.run(gather_all())


# funcion para la busqueda por proveedor en especifico
def fetch_products_proveedor(proveedor: str, search: str, limit: int = 20):
    search = search.lower()
    proveedor = proveedor.lower()

    # esto devuelve el metodo scrapper de cada proveedor
    scraper = PROVEEDORES.get(proveedor)
    if not scraper:
        raise RuntimeError(f"Proveedor '{proveedor}' no soportado")

    # esto es para comprobar si es un metodo async o sync del scraper
    if asyncio.iscoroutinefunction(scraper):
        # realiza la busqueda en el proveedor en especifico
        return asyncio.run(scraper(search, limit))
    else:
        return scraper(search, limit)


# funcion para la busqueda por ciudad
def fetch_products_by_ciudad(ciudad: str, search: str, limit: int = 20):

    ciudad = ciudad.lower()
    search = search.lower()

    # Obtener lista de proveedores según la ciudad
    proveedores = CIUDAD_PROVEEDORES.get(ciudad, [])
    if not proveedores:
        raise RuntimeError(f"No hay scrapers configurados para la ciudad '{ciudad}'")

    async def gather_selected():
        tasks = []
        sync_results = []

        for proveedor in proveedores:
            scraper = PROVEEDORES.get(proveedor)
            if not scraper:
                continue

            if asyncio.iscoroutinefunction(scraper):
                tasks.append(scraper(search, limit))
            else:
                try:
                    sync_results.append(scraper(search, limit))
                except Exception as e:
                    print(f"Error en scraper {proveedor}: {e}")

        async_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for sublist in async_results + sync_results:
            if isinstance(sublist, list):
                all_items.extend(sublist)

        return all_items[:limit]

    return asyncio.run(gather_selected())
