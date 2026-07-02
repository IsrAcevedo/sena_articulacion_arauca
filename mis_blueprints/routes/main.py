from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from consultas import consulta,insertar



main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def inicio():
    query1 = "SELECT id_proyectos AS id, nombre, descripcion_corta AS descripcion, foto_principal AS foto FROM proyectos"
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios"
    query4 = "SELECT id_instructor AS id, nombres, apellidos,id_profesion, foto FROM instructor"
    proyectos = consulta(query1)
    colegios = consulta(query2)
    municipios = consulta(query3)
    instructores = consulta(query4)
    return render_template('index.html', proyectos = proyectos, colegios = colegios, municipios = municipios , instructores = instructores)


@main_bp.route('/proyecto/<int:id>')
def proyecto(id):
    print(id)
    query = "SELECT * FROM proyectos WHERE id_proyectos = %s"
    parametros = id,
    proyecto = consulta(query, parametros)
    return render_template('proyectos.html', proyecto = proyecto)

@main_bp.route('/municipio/<int:id>')
def municipio(id):
    query = "SELECT * FROM municipios WHERE id_municipios = %s"
    parametros = id,
    municipio = consulta(query, parametros)
    return render_template('municipios.html', municipio = municipio)

@main_bp.route('/colegios')
def colegios():
    query = 'SELECT c.id_colegios AS id, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio FROM colegios c INNER JOIN municipios m ON m.id_municipios = c.id_municipios'
    colegios = consulta(query)
    return render_template('colegios.html', colegios= colegios)


@main_bp.route('/colegio/<id>')
def colegio(id):
    query = 'SELECT * FROM colegios WHERE id_colegios= %s'
    parametros = id,
    colegio = consulta(query, parametros)[0]
    return render_template('colegio.html', colegio=colegio)


@main_bp.route('/instructor/<int:id>')
def instructor(id):
    query = 'SELECT * FROM instructor WHERE id_instructor = %s'
    parametros = id,
    instructor = consulta(query, parametros)[0]
    return render_template('instructor.html', instructor = instructor)



