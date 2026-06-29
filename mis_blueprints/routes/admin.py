from flask import Blueprint
from consultas import consulta, insertar
from decoradores import login_requerido
import os
from werkzeug.utils import secure_filename
import uuid



admin_bp = Blueprint('admin', __name__,  url_prefix='/admin')


# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
# ALLOWED_EXTENSIONS = {'webp'}


# os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# def nombre_imagen(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def guardar_imagen(file, carpeta_destino):
#     if file and nombre_imagen(file.filename):
#         filename = secure_filename(file.filename)
#         extension = filename.rsplit('.', 1)[1].lower()

#         nuevo_nombre = f"{uuid.uuid4().hex}.{extension}"
#         ruta_completa = os.path.join(carpeta_destino, nuevo_nombre)

#         file.save(ruta_completa)

#         return nuevo_nombre  

#     return None



@admin_bp.route('/dashborad')
@login_requerido
def admin():
    
    query1 ="SELECT COUNT(*) AS colegios FROM colegios"
    query2 ="SELECT COUNT(*) AS proyectos FROM proyectos "
    query3 ="SELECT COUNT(*) AS instructores FROM instructor "
    colegios= consulta(query1)
    proyectos= consulta(query2)
    instructores= consulta(query3)
    registros= [colegios,proyectos,instructores]
    return render_template('panel.html', registros = registros )

@admin_bp.route('/crear_cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'POST':
        aprendices={'1157963293','1115732838','1094267349', '1157963279','1127622165'}
        doc = request.form.get('id')
        nombres = request.form.get('name')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        confirm_password =  request.form.get('confirm_password')
        foto = request.files.get('foto')
    
        if doc in aprendices:
            if password != confirm_password:
                flash('Las contraseñas no coinciden.', 'error')
                return redirect(request.url)

            if foto and nombre_imagen(foto.filename):
                filename = secure_filename(foto.filename)
                extension = filename.rsplit('.', 1)[1].lower()
                nuevo_nombre = f"{uuid.uuid4().hex}.{extension}"
                ruta_foto = os.path.join(app.config['UPLOAD_FOLDER'], nuevo_nombre)
                foto.save(ruta_foto)
            else:
                flash('Formato de imagen no permitido. Solo .webp', 'error')
                return redirect(request.url)

            query = "INSERT INTO usuarios (nombre_completo, nombre_usuario, numero_identificacion, foto_perfil,password_hash) VALUES (%s,%s,%s,%s,%s)"
            password_hash=generate_password_hash(password)
            parametros = (nombres, usuario, doc, nuevo_nombre, password_hash)
            insertar(query,parametros)

            flash('Registro exitoso', 'success')
            return redirect(url_for('login'))
        else:
            flash('No tienes permiso de crear una cuenta', 'error')
            return redirect(request.url)
    
    return render_template('crear_cuenta.html')

@admin_bp.route('/agregar_colegio', methods=['GET','POST'])
def agregar_colegio():
    if request.method == 'POST':
        colegio = request.form.get('colegio')
        logo = request.files.get('logo')
        municipio = request.form.get('municipio')
        nombre_logo = guardar_imagen(logo, app.config['UPLOAD_FOLDER'])
        if not nombre_logo:
            flash('formato de imagen no permitido', 'error')
            return redirect(request.url)
        query = 'INSERT INTO colegios (id_municipios, nombre, logo) VALUES (%s,%s,%s)'
        parametros = (municipio, colegio, nombre_logo)
        guardar = insertar(query, parametros)
        if guardar:
            flash(guardar)
            return redirect(request.url)
    query = 'SELECT id_municipios AS id, nombre FROM municipios'
    municipios = consulta(query)    
    return render_template('agregar_colegio.html', municipios = municipios)


@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        documento = request.form['documento']
        password = request.form['password']
        query = "SELECT numero_identificacion, password_hash,nombre_usuario FROM usuarios WHERE numero_identificacion = %s"
        parametros = (documento,)
        respuesta = consulta(query, parametros)

        if respuesta:
            usuario=respuesta[0]
            contra=usuario['password_hash']

            if check_password_hash(contra, password):
                session['documento']=usuario['numero_identificacion']
                session['user']=usuario['nombre_usuario']
                return redirect(url_for('admin')) 
            else:
                flash('Contraseña incorrecta.', 'error')
        else:
            flash('Usuario no encontrado.', 'error')
   
    return render_template('login.html')
   
  


@admin_bp.route('/logout')
def logout():
    session.pop('documento', None)  
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('inicio')) 
