from flask import Flask
from mis_blueprints.routes import main_bp, admin_bp
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


    app.secret_key = os.getenv('API_KEY')

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
