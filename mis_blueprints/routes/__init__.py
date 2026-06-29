# Importar blueprints
from .main import main_bp
from .admin import admin_bp

# Exportar para que app.py pueda usarlos
__all__ = ['main_bp', 'admin_bp']
