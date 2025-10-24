from app import create_app
from flask_cors import CORS
from app.routes.products import products
from app.routes.consumerProducts import consumerProducts
# from flasgger import Swagger

app = create_app()

CORS(app)
app.register_blueprint(products)
app.register_blueprint(consumerProducts)

@app.errorhandler(404)
def not_found(error):
    return {"error": "Ruta no encontrada"}, 404


@app.errorhandler(Exception)
def handle_error(e):
    return {"error": str(e)}, 500


@app.route("/health")
def health():
    return {"status": "ok"}, 200


# Router index
@app.get("/")
def index():
    return {"message": "Scraper products is running."}
# swagger = Swagger(
#         app,
#         template={
#             "info": {
#                 "title": "SCRAPER-PRODUCTS API",
#                 "description": "Documentaion of api ",
#                 "version": "1.0.0",
#             }
#         },
#     )

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

