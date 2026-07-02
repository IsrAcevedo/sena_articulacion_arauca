from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'documento' not in session:
            flash('Iniciar Sesion', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorada

def rol_requerido(rol_necesario):
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if 'documento' not in session or 'rol' not in session:
                flash('Iniciar Sesion', 'error')
                return redirect(url_for('admin.login'))

            if session['rol'] != rol_necesario:
                flash('No tienes permiso para acceder a esta sección.', 'error')
                return redirect(url_for('main.inicio'))  

            return f(*args, **kwargs)
        return decorada
    return decorador
