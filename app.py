from flask import Flask,  render_template
from consultas import consulta
app = Flask(__name__)

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

