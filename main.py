from app import create_app
from flask_cors import CORS
from app.routes.products import products

app = create_app()

CORS(app)
app.register_blueprint(products)


@app.errorhandler(404)
def not_found(error):
    return {"error": "Ruta no encontrada"}, 404

@app.route('/health')
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)