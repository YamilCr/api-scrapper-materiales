from flask import Blueprint, jsonify, request
from app.controllers.controllerProduct import fetch_all_products, fetch_products_proveedor

products = Blueprint('products', __name__, url_prefix='/products')

@products.route('/search', methods=['GET'])
def search_products():
    search = request.args.get('search')
    limit = int(request.args.get('limit', 30))

    if not search:
        return jsonify({"error": "Parámetro 'search' es requerido"}), 400

    if not (1 <= limit <= 100):
        return jsonify({"error": "El parámetro 'limit' debe estar entre 1 y 100"}), 400

    productos = fetch_all_products(search, limit)
    return jsonify({
        "query": search,
        "total": len(productos),
        "items": productos
    })

@products.route('/search/<proveedor>', methods=['GET'])
def search_for_proveedor(proveedor):
    search = request.args.get('search')
    limit = int(request.args.get('limit', 20))

    proveedores_validos = {"easy", "montessi", "neomat", "forte"}

    if proveedor.lower() not in proveedores_validos:
        return jsonify({"error": f"Proveedor '{proveedor}' no es válido"}), 400

    if not search:
        return jsonify({"error": "Parámetro 'search' es requerido"}), 400

    if not (1 <= limit <= 100):
        return jsonify({"error": "El parámetro 'limit' debe estar entre 1 y 100"}), 400

    productos = fetch_products_proveedor(proveedor.lower(), search, limit)
    return jsonify({
        "query": search,
        "total": len(productos),
        "items": productos
    })