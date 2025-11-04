from flask import Flask,  render_template, session, url_for, redirect, flash, request
from consultas import consulta,insertar
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename
from decoradores import login_requerido

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv('API_KEY')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def nombre_imagen(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def inicio():
    # query='SELECT * FROM municipios'
    # municipios = consulta(query)
   
    return render_template('index.html')
@app.route('/proyectos')
def proyectos():
    query="SELECT nombre FROM colegios"
    colegios = consulta(query)
    return render_template('proyectos.html', colegios=colegios)

@app.route('/municipios')
def municipios():
   # query="SELECT nombre FROM colegios"
    #colegios = consulta(query)
    return render_template('municipios.html')

@app.route('/colegios')
def colegios():
   # query="SELECT nombre FROM colegios"
    #colegios = consulta(query)
    return render_template('colegios.html')


@app.route('/colegio')
def colegio():
   
    return render_template('colegio.html')


@app.route('/instructor')
def instructor():
   
    return render_template('instructor.html')

@app.route('/admin')
@login_requerido
def admin():
    
    return render_template('panel.html')

@app.route('/crear_cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'POST':
        aprendices={'1157963293','1094267349','1094267349', '1157963279','1127622165'}
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

@app.route('/login', methods=['GET','POST'])
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
   
  


@app.route('/logout')
def logout():
    session.pop('documento', None)  
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('inicio')) 
