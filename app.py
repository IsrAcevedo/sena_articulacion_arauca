from flask import Flask
from mis_blueprints.routes import main_bp, admin_bp
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    # SECRET_KEY es el nombre estándar; API_KEY se admite para instalaciones antiguas.
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('API_KEY')

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
