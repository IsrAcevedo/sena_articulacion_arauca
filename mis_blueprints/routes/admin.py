from flask import request, Blueprint, render_template, flash, redirect, url_for, session, jsonify
from consultas import consulta, insertar
from decoradores import login_requerido
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import uuid



admin_bp = Blueprint('admin', __name__,  url_prefix='/admin')


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'webp'}


os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def nombre_imagen(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_imagen(file, carpeta_destino, subcarpeta=''):
    if file and nombre_imagen(file.filename):
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()

        nuevo_nombre = f"{uuid.uuid4().hex}.{extension}"
        ruta_subcarpeta = os.path.join(carpeta_destino, subcarpeta) if subcarpeta else carpeta_destino
        os.makedirs(ruta_subcarpeta, exist_ok=True)
        ruta_completa = os.path.join(ruta_subcarpeta, nuevo_nombre)

        file.save(ruta_completa)

        return f"{subcarpeta}/{nuevo_nombre}" if subcarpeta else nuevo_nombre

    return None


# ruta panel principal

@admin_bp.route('/dashboard')
@login_requerido
def dashboard():
    query = "SELECT (SELECT COUNT(*) FROM colegios) AS colegios,(SELECT COUNT(*) FROM proyectos) AS proyectos,(SELECT COUNT(*) FROM instructor) AS instructores;"
    estadisticas = consulta(query)
    print(estadisticas)
    return render_template('admin/panel.html', estadisticas = estadisticas)

#ruta para administrar  proyectos
@admin_bp.route('/proyectos')
@login_requerido
def proyectos():
    query = "SELECT p.id_proyectos AS id, p.nombre, p.descripcion_corta AS descripcion, t.nombre AS tecnico, p.fecha_inicio FROM proyectos AS p INNER JOIN tecnicos AS t ON t.id_tecnicos = p.id_tecnico"
    proyectos = consulta(query)
    query_tecnicos = "SELECT id_tecnicos AS id, nombre FROM tecnicos"
    lista_tecnicos = consulta(query_tecnicos)
    return render_template('admin/proyectos.html', proyectos = proyectos, lista_tecnicos = lista_tecnicos)

#ruta para crear proyecto
@admin_bp.route('/proyectos/crear', methods=['POST'])
@login_requerido
def crear_proyecto():
    nombre = request.form.get('nombre')
    descripcion_corta = request.form.get('descripcion_corta')
    descripcion_larga = request.form.get('descripcion_larga')
    objetivo = request.form.get('objetivo')
    resultado = request.form.get('resultado')
    tecnico = request.form.get('tecnico')
    foto_principal = request.files.get('foto_principal')
    video_intro = request.form.get('video_intro')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    activo = request.form.get('activo', '1')
    
    if foto_principal and foto_principal.filename:
        nombre_foto = guardar_imagen(foto_principal, UPLOAD_FOLDER, 'proyectos')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
    else:
        nombre_foto = 'imagen.webp'
    
    query = "INSERT INTO proyectos (id_tecnico, nombre, descripcion_corta, descripcion_larga, objetivo, resultado, foto_principal, video_intro, fecha_inicio, fecha_fin, activo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    parametros = (tecnico, nombre, descripcion_corta, descripcion_larga, objetivo, resultado, nombre_foto, video_intro, fecha_inicio, fecha_fin, activo)
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para editar proyecto
@admin_bp.route('/proyectos/editar/<int:id>', methods=['POST'])
@login_requerido
def editar_proyecto(id):
    nombre = request.form.get('nombre')
    descripcion_corta = request.form.get('descripcion_corta')
    descripcion_larga = request.form.get('descripcion_larga')
    objetivo = request.form.get('objetivo')
    resultado = request.form.get('resultado')
    tecnico = request.form.get('tecnico')
    foto_principal = request.files.get('foto_principal')
    video_intro = request.form.get('video_intro')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    activo = request.form.get('activo', '1')
    
    if foto_principal and foto_principal.filename:
        nombre_foto = guardar_imagen(foto_principal, UPLOAD_FOLDER, 'proyectos')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
        query = "UPDATE proyectos SET id_tecnico = %s, nombre = %s, descripcion_corta = %s, descripcion_larga = %s, objetivo = %s, resultado = %s, foto_principal = %s, video_intro = %s, fecha_inicio = %s, fecha_fin = %s, activo = %s WHERE id_proyectos = %s"
        parametros = (tecnico, nombre, descripcion_corta, descripcion_larga, objetivo, resultado, nombre_foto, video_intro, fecha_inicio, fecha_fin, activo, id)
    else:
        query = "UPDATE proyectos SET id_tecnico = %s, nombre = %s, descripcion_corta = %s, descripcion_larga = %s, objetivo = %s, resultado = %s, video_intro = %s, fecha_inicio = %s, fecha_fin = %s, activo = %s WHERE id_proyectos = %s"
        parametros = (tecnico, nombre, descripcion_corta, descripcion_larga, objetivo, resultado, video_intro, fecha_inicio, fecha_fin, activo, id)
    
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})


#ruta para administar programas
@admin_bp.route('/programas')
@login_requerido
def programas():
    query = "SELECT t.id_tecnicos AS id, t.nombre  AS nombre, CONCAT(i.nombres,' ',i.apellidos) AS instructor, c.nombre AS colegio, COUNT(p.id_proyectos) AS num_proyectos, COUNT(a.id_aprendices) AS num_aprendices FROM tecnicos AS t LEFT JOIN instructor AS i ON i.id_instructor = t.id_instructor LEFT JOIN colegios AS c ON c.id_colegios = t.id_colegio LEFT JOIN proyectos AS p ON p.id_tecnico = t.id_tecnicos LEFT JOIN aprendices AS a ON a.id_tecnico = t.id_tecnicos GROUP BY t.id_tecnicos"
    programas = consulta(query)
    print(programas)
    return render_template('admin/programas.html', programas=programas)


#ruta para administar  colegios
@admin_bp.route('/colegios')
@login_requerido
def colegios():
    query = "SELECT c.id_colegios AS id, c.nombre, m.nombre AS municipio, (SELECT COUNT(*) FROM tecnicos WHERE id_colegio = c.id_colegios) AS num_tecnicos, (SELECT COUNT(*) FROM proyectos p INNER JOIN tecnicos t ON p.id_tecnico = t.id_tecnicos WHERE t.id_colegio = c.id_colegios) AS num_proyectos FROM colegios AS c INNER JOIN municipios AS m ON m.id_municipios = c.id_municipios "
    colegios = consulta(query)
    query_municipios = "SELECT id_municipios AS id, nombre FROM municipios WHERE activo = 1"
    lista_municipios = consulta(query_municipios)
    return render_template('admin/colegios.html', colegios = colegios, lista_municipios = lista_municipios)

#ruta para crear colegio
@admin_bp.route('/colegios/crear', methods=['POST'])
@login_requerido
def crear_colegio():
    nombre = request.form.get('nombre')
    slogan = request.form.get('slogan')
    municipio = request.form.get('municipio')
    logo = request.files.get('logo')
    activo = request.form.get('activo', '1')
    
    if logo and logo.filename:
        nombre_logo = guardar_imagen(logo, UPLOAD_FOLDER, 'colegios')
        if not nombre_logo:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
    else:
        nombre_logo = 'imagen.webp'
    
    query = "INSERT INTO colegios (id_municipios, nombre, slogan, logo, activo) VALUES (%s, %s, %s, %s, %s)"
    parametros = (municipio, nombre, slogan, nombre_logo, activo)
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para editar colegio
@admin_bp.route('/colegios/editar/<int:id>', methods=['POST'])
@login_requerido
def editar_colegio(id):
    nombre = request.form.get('nombre')
    slogan = request.form.get('slogan')
    municipio = request.form.get('municipio')
    logo = request.files.get('logo')
    activo = request.form.get('activo', '1')
    
    if logo and logo.filename:
        nombre_logo = guardar_imagen(logo, UPLOAD_FOLDER, 'colegios')
        if not nombre_logo:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
        query = "UPDATE colegios SET id_municipios = %s, nombre = %s, slogan = %s, logo = %s, activo = %s WHERE id_colegios = %s"
        parametros = (municipio, nombre, slogan, nombre_logo, activo, id)
    else:
        query = "UPDATE colegios SET id_municipios = %s, nombre = %s, slogan = %s, activo = %s WHERE id_colegios = %s"
        parametros = (municipio, nombre, slogan, activo, id)
    
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})




#ruta para administrar  instructores
@admin_bp.route('/instructores')
@login_requerido
def instructores():
    query = "SELECT i.id_instructor AS id, i.nombres, i.apellidos, p.nombre_profesion AS profesion, (SELECT COUNT(*) FROM proyectos pr INNER JOIN tecnicos t ON pr.id_tecnico = t.id_tecnicos WHERE t.id_instructor = i.id_instructor) AS num_proyectos FROM instructor AS i LEFT JOIN profesiones p ON i.id_profesion = p.id_profesion"
    instructores = consulta(query)
    query_profesiones = "SELECT id_profesion AS id, nombre_profesion FROM profesiones"
    lista_profesiones = consulta(query_profesiones)
    return render_template('admin/instructores.html', instructores = instructores, lista_profesiones = lista_profesiones)

#ruta para crear instructor
@admin_bp.route('/instructores/crear', methods=['POST'])
@login_requerido
def crear_instructor():
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    profesion = request.form.get('profesion')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'instructor')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
    else:
        nombre_foto = 'imagen.webp'
    
    query = "INSERT INTO instructor (id_profesion, nombres, apellidos, foto, activo) VALUES (%s, %s, %s, %s, %s)"
    parametros = (profesion, nombres, apellidos, nombre_foto, activo)
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para editar instructor
@admin_bp.route('/instructores/editar/<int:id>', methods=['POST'])
@login_requerido
def editar_instructor(id):
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    profesion = request.form.get('profesion')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'instructor')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
        query = "UPDATE instructor SET id_profesion = %s, nombres = %s, apellidos = %s, foto = %s, activo = %s WHERE id_instructor = %s"
        parametros = (profesion, nombres, apellidos, nombre_foto, activo, id)
    else:
        query = "UPDATE instructor SET id_profesion = %s, nombres = %s, apellidos = %s, activo = %s WHERE id_instructor = %s"
        parametros = (profesion, nombres, apellidos, activo, id)
    
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})


#ruta para administrar aprendices
@admin_bp.route('/aprendices')
@login_requerido
def aprendices():
    query = "SELECT a.id_aprendices AS id, CONCAT(a.nombres, ' ', a.apellidos) AS nombre, t.nombre AS tecnico, c.nombre AS colegio, p.nombre AS proyecto, a.activo AS estado FROM aprendices AS a INNER JOIN tecnicos AS t ON t.id_tecnicos = a.id_tecnico INNER JOIN colegios AS c ON c.id_colegios = t.id_colegio LEFT JOIN proyectos AS p ON p.id_tecnico = t.id_tecnicos"
    aprendices = consulta(query)
    query_tecnicos = "SELECT id_tecnicos AS id, nombre FROM tecnicos"
    lista_tecnicos = consulta(query_tecnicos)
    return render_template('admin/aprendices.html', aprendices = aprendices, lista_tecnicos = lista_tecnicos)

#ruta para crear aprendiz
@admin_bp.route('/aprendices/crear', methods=['POST'])
@login_requerido
def crear_aprendiz():
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    numero_identificacion = request.form.get('numero_identificacion')
    tecnico = request.form.get('tecnico')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'aprendiz')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
    else:
        nombre_foto = 'imagen.webp'
    
    query = "INSERT INTO aprendices (id_tecnico, nombres, apellidos, numero_identificacion, foto, activo) VALUES (%s, %s, %s, %s, %s, %s)"
    parametros = (tecnico, nombres, apellidos, numero_identificacion, nombre_foto, activo)
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para editar aprendiz
@admin_bp.route('/aprendices/editar/<int:id>', methods=['POST'])
@login_requerido
def editar_aprendiz(id):
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    numero_identificacion = request.form.get('numero_identificacion')
    tecnico = request.form.get('tecnico')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'aprendiz')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
        query = "UPDATE aprendices SET id_tecnico = %s, nombres = %s, apellidos = %s, numero_identificacion = %s, foto = %s, activo = %s WHERE id_aprendiz = %s"
        parametros = (tecnico, nombres, apellidos, numero_identificacion, nombre_foto, activo, id)
    else:
        query = "UPDATE aprendices SET id_tecnico = %s, nombres = %s, apellidos = %s, numero_identificacion = %s, activo = %s WHERE id_aprendiz = %s"
        parametros = (tecnico, nombres, apellidos, numero_identificacion, activo, id)
    
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para administrar  municipios
@admin_bp.route('/municipios')
@login_requerido
def municipios():
    query = "SELECT m.id_municipios AS id, m.nombre AS nombre, (SELECT COUNT(*) FROM colegios WHERE id_municipios = m.id_municipios) AS num_colegios, (SELECT COUNT(*) FROM proyectos p INNER JOIN tecnicos t ON p.id_tecnico = t.id_tecnicos INNER JOIN colegios c ON t.id_colegio = c.id_colegios WHERE c.id_municipios = m.id_municipios) AS num_proyectos FROM municipios AS m"
    municipios = consulta(query)
    return render_template('admin/municipios.html', municipios = municipios)

#ruta para crear municipio
@admin_bp.route('/municipios/crear', methods=['POST'])
@login_requerido
def crear_municipio():
    nombre = request.form.get('nombre')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'municipios')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
    else:
        nombre_foto = 'imagen.webp'
    
    query = "INSERT INTO municipios (nombre, foto, activo) VALUES (%s, %s, %s)"
    parametros = (nombre, nombre_foto, activo)
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})

#ruta para editar municipio
@admin_bp.route('/municipios/editar/<int:id>', methods=['POST'])
@login_requerido
def editar_municipio(id):
    nombre = request.form.get('nombre')
    foto = request.files.get('foto')
    activo = request.form.get('activo', '1')
    
    if foto and foto.filename:
        nombre_foto = guardar_imagen(foto, UPLOAD_FOLDER, 'municipios')
        if not nombre_foto:
            return jsonify({'success': False, 'message': 'Formato de imagen no permitido. Solo .webp'})
        query = "UPDATE municipios SET nombre = %s, foto = %s, activo = %s WHERE id_municipios = %s"
        parametros = (nombre, nombre_foto, activo, id)
    else:
        query = "UPDATE municipios SET nombre = %s, activo = %s WHERE id_municipios = %s"
        parametros = (nombre, activo, id)
    
    resultado = insertar(query, parametros)
    return jsonify({'success': True, 'message': resultado})


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
    
    return render_template('admin/crear_cuenta.html')



@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        documento = request.form['documento']
        password = request.form['password']
        query = "SELECT numero_identificacion, password_hash, nombre_usuario, foto_perfil FROM usuarios WHERE numero_identificacion = %s"
        parametros = (documento,)
        respuesta = consulta(query, parametros)

        if respuesta:
            usuario=respuesta[0]
            contra=usuario['password_hash']

            if check_password_hash(contra, password):
                session['documento']=usuario['numero_identificacion']
                session['user']=usuario['nombre_usuario']
                session['foto_perfil']=usuario['foto_perfil']
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Contraseña incorrecta.', 'error')
        else:
            flash('Usuario no encontrado.', 'error')
   
    return render_template('admin/login.html')
   

@admin_bp.route('/logout')
def logout():
    session.pop('documento', None)  
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('main.inicio')) 
