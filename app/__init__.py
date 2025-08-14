from flask import Flask
# from flask_restx import Api
# from app.routes.products import api as products_ns
# from app.database.config import Config
# from app.database.database import init_db

def create_app():
    app = Flask(__name__)

    # 🔧 Configuración de base de datos (descomenta si lo usás)
    # app.config.from_object(Config)
    # init_db(app)

    # # 📘 Inicialización de Flask-RESTX
    # api = Api(
    #     app,
    #     version='1.0',
    #     title='API-Materiales',
    #     description='API REST para búsqueda de materiales de construcción',
    #     doc='/docs'  # Cambia la ruta de Swagger si querés algo más personalizado
    # )

    # # 📦 Registro de namespaces
    # api.add_namespace(products_ns, path='/products')

    return app