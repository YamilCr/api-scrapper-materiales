from app.routes import products

def register_routes(app):
    app.register_blueprint(products)