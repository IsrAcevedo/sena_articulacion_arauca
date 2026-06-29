from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from consultas import consulta,insertar
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
import uuid
from werkzeug.utils import secure_filename





main_bp = Blueprint('main', __name__)

  

@main_bp.route('/')
def inicio():
    # query='SELECT * FROM municipios'
    # municipios = consulta(query)
   
    return render_template('index.html')
@main_bp.route('/proyectos')
def proyectos():
    query="SELECT nombre FROM colegios"
    colegios = consulta(query)
    return render_template('proyectos.html', colegios=colegios)

@main_bp.route('/municipios')
def municipios():
   # query="SELECT nombre FROM colegios"
    #colegios = consulta(query)
    return render_template('municipios.html')

@main_bp.route('/colegios')
def colegios():
    query = 'SELECT c.id_colegios AS id, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio FROM colegios c INNER JOIN municipios m ON m.id_municipios = c.id_municipios'
    colegios = consulta(query)
    return render_template('colegios.html', colegios= colegios)


@main_bp.route('/colegio<id>')
def colegio(id):
    query = 'SELECT nombre, logo FROM colegios WHERE id_colegios= %s'
    parametros = id,
    colegio = consulta(query, parametros)
    return render_template('colegio.html', colegio=colegio)


@main_bp.route('/instructor')
def instructor():
   
    return render_template('instructor.html')



