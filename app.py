# app.py
from flask import Flask
from flask_cors import CORS  # Importar CORS
from views.main import main_bp
from controllers.hospital_controller import hospital_controller_bp
from controllers.almacen_controller import warehouse_controller_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Inicializar CORS para la aplicación completa

    # Registro de blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(hospital_controller_bp, url_prefix='/api')
    app.register_blueprint(warehouse_controller_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)