from app.services.webScraperEasy import fetch_data_layer_items
from app.services.webScraperMontessi import fetch_data_items_montessi
from app.services.webScraperForte import fetch_data_items_forte
from app.services.webScraperNeoMat import fetch_data_items_neomat
from app.services.webScraperML import fetch_data_items_ml
import asyncio

# Diccionario de funciones por proveedor
PROVEEDORES = {
    "easy": fetch_data_layer_items,
    "montessi": fetch_data_items_montessi,
    "forte": fetch_data_items_forte,
    "neomat": fetch_data_items_neomat,
    "meli": fetch_data_items_ml,
}

def fetch_all_products(search: str, limit: int = 50):
    search = search.lower()

    # Ejecutamos funciones async desde sync usando asyncio.run()
    async def gather_all():
        tasks = [
            # fetch_data_layer_items(search, 15),
            fetch_data_items_montessi(search, 5),
            fetch_data_items_forte(search, 5),
            fetch_data_items_neomat(search, 5),
            # fetch_data_items_ml(search,15)
        ]
        # try:
        #     results_easy = await fetch_data_layer_items(search, 10)
        # except Exception as e:
        #     print(f"[Easy] Error al obtener productos: {e}")
        #     results_easy = []
        
        results = await asyncio.gather(*tasks)
        # results.append(results_easy)
        all_items = [item for sublist in results for item in sublist]
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