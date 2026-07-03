from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        # 1. Verificar si el usuario ha iniciado sesión
        if 'documento' not in session:
            flash('Iniciar Sesión', 'error')
            return redirect(url_for('admin.login'))
        
        rol = session.get('rol')
        
        # 2. El rol 'usuario' no debe acceder a ninguna ruta protegida del blueprint 'admin'
        if request.blueprint == 'admin' and rol == 'usuario':
            flash('No tienes permiso para acceder a la administración.', 'error')
            return redirect(url_for('main.inicio'))
        
        # 3. El rol 'admin' tiene restricciones en rutas 'eliminar' / 'delete'
        if rol == 'admin':
            es_ruta_eliminar = (
                'eliminar' in request.path.lower() or 
                'delete' in request.path.lower() or 
                'eliminar' in f.__name__.lower() or
                'delete' in f.__name__.lower()
            )
            if es_ruta_eliminar:
                flash('No tienes permiso para realizar esta acción de eliminación.', 'error')
                return redirect(url_for('admin.dashboard'))
                
        return f(*args, **kwargs)
    return decorada

def rol_requerido(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            # 1. Verificar si el usuario ha iniciado sesión
            if 'documento' not in session or 'rol' not in session:
                flash('Iniciar Sesión', 'error')
                return redirect(url_for('admin.login'))

            rol = session.get('rol')
            
            # 2. Verificar si el rol del usuario está permitido
            if rol not in roles_permitidos:
                flash('No tienes permiso para acceder a esta sección.', 'error')
                return redirect(url_for('main.inicio'))  

            # 3. Si el rol es 'admin', aplicar restricciones de eliminación
            if rol == 'admin':
                es_ruta_eliminar = (
                    'eliminar' in request.path.lower() or 
                    'delete' in request.path.lower() or 
                    'eliminar' in f.__name__.lower() or
                    'delete' in f.__name__.lower()
                )
                if es_ruta_eliminar:
                    flash('No tienes permiso para realizar esta acción de eliminación.', 'error')
                    return redirect(url_for('admin.dashboard'))

            return f(*args, **kwargs)
        return decorada
    return decorador

