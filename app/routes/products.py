
from flask_restx import Namespace, Resource, fields, reqparse
from app.controllers.controllerProduct import fetch_all_products, fetch_products_proveedor

api = Namespace('products', description='Operaciones de búsqueda de productos')

# ✅ Modelo de respuesta (puedes ajustarlo según la estructura real de tus productos)
producto_model = api.model('Producto', {
    'product_id': fields.String(description="ID del producto"),
    'name': fields.String(required=True, description="Nombre del producto"),
    'price_short': fields.String(description="Precio en formato corto"),
    'price_number': fields.Float(description="Precio como número"),
    'image_url': fields.String(description="URL de la imagen del producto"),
    'link': fields.String(description="Enlace al producto"),
    'stock': fields.String(description="Estado de stock"),
    'source': fields.String(description="Fuente del producto (ej. Easy)"),
    'brandName': fields.String(description="Marca del producto"),
    'category': fields.String(description="Categoría del producto"),
    'discountPercentage': fields.Float(description="Porcentaje de descuento"),
    'logo': fields.String(description="URL del logo del proveedor"),
})


# ✅ Parser para query params
search_parser = reqparse.RequestParser()
search_parser.add_argument('search', type=str, required=True, help="Texto de búsqueda")
search_parser.add_argument('limit', type=int, default=30, help="Cantidad máxima de resultados (1-30)")

# 🧭 Ruta: /products/search
@api.route('/search')
class SearchProducts(Resource):
    @api.expect(search_parser)
    @api.marshal_with(api.model('ResultadoBusqueda', {
        'query': fields.String,
        'total': fields.Integer,
        'items': fields.List(fields.Nested(producto_model))
    }))
    def get(self):
        args = search_parser.parse_args()
        search = args['search']
        limit = args['limit']
        productos = fetch_all_products(search, limit)
        return {
            "query": search,
            "total": len(productos),
            "items": productos
        }

# 🧭 Ruta: /products/search/<proveedor>
@api.route('/search/<string:proveedor>')
@api.param('proveedor', 'Nombre del proveedor (easy, montessi, neomat, forte)')
class SearchByProveedor(Resource):
    @api.expect(search_parser)
    @api.marshal_with(api.model('ResultadoProveedor', {
        'query': fields.String,
        'total': fields.Integer,
        'items': fields.List(fields.Nested(producto_model))
    }))
    def get(self, proveedor):
        args = search_parser.parse_args()
        search = args['search']
        limit = args['limit']
        proveedores_validos = {"easy", "montessi", "neomat", "forte"}

        if proveedor.lower() not in proveedores_validos:
            api.abort(400, f"Proveedor '{proveedor}' no es válido")

        productos = fetch_products_proveedor(proveedor.lower(), search, limit)
        return {
            "query": search,
            "total": len(productos),
            "items": productos
        }
        


# from flask import Blueprint, jsonify, request
# from app.controllers.controllerProduct import fetch_all_products, fetch_products_proveedor

# products = Blueprint('products', __name__, url_prefix='/products')
# # @products.route('/search', methods=['GET'])
# # def hello():
# #     return jsonify({"message": "Hola desde Flask modular!"})

# @products.route('/search', methods=['GET'])
# def search_products():
#     search = request.args.get('search')
#     limit = int(request.args.get('limit', 30))

#     if not search:
#         return jsonify({"error": "Parámetro 'search' es requerido"}), 400

#     if not (1 <= limit <= 100):
#         return jsonify({"error": "El parámetro 'limit' debe estar entre 1 y 100"}), 400

#     productos = fetch_all_products(search, limit)
#     return jsonify({
#         "query": search,
#         "total": len(productos),
#         "items": productos
#     })

# @products.route('/search/<proveedor>', methods=['GET'])
# def search_for_proveedor(proveedor):
#     search = request.args.get('search')
#     limit = int(request.args.get('limit', 20))

#     proveedores_validos = {"easy", "montessi", "neomat", "forte"}

#     if proveedor.lower() not in proveedores_validos:
#         return jsonify({"error": f"Proveedor '{proveedor}' no es válido"}), 400

#     if not search:
#         return jsonify({"error": "Parámetro 'search' es requerido"}), 400

#     if not (1 <= limit <= 100):
#         return jsonify({"error": "El parámetro 'limit' debe estar entre 1 y 100"}), 400

#     productos = fetch_products_proveedor(proveedor.lower(), search, limit)
#     return jsonify({
#         "query": search,
#         "total": len(productos),
#         "items": productos
#     })