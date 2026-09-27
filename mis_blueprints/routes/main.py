from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from consultas import consulta,insertar



main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def inicio():
    query1 = "SELECT id_proyectos AS id, nombre, descripcion_corta AS descripcion, foto_principal AS foto FROM proyectos limit 3"
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios limit 3"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios WHERE activo = 1"
    query4 = "SELECT i.id_instructor AS id, i.nombres, i.apellidos, p.nombre_profesion as profesion, i.foto FROM instructor i INNER JOIN profesiones p ON i.id_profesion=p.id_profesion limit 4"
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


@main_bp.route('/instructores')
def instructores():
    query = "SELECT i.id_instructor AS id, i.foto AS foto, CONCAT(i.nombres, ' ', i.apellidos) AS nombre, p.nombre_profesion AS profesion, (SELECT GROUP_CONCAT(DISTINCT t.id_modalidad ORDER BY t.id_modalidad SEPARATOR ',') FROM tecnicos t WHERE t.id_instructor = i.id_instructor) AS areas_ids, (SELECT GROUP_CONCAT(DISTINCT m.nombre ORDER BY m.nombre SEPARATOR '|') FROM tecnicos t2 INNER JOIN modalidad m ON m.id_modalidad = t2.id_modalidad WHERE t2.id_instructor = i.id_instructor) AS areas_nombres, (SELECT GROUP_CONCAT(DISTINCT mu.nombre ORDER BY mu.nombre SEPARATOR '|') FROM tecnicos t3 INNER JOIN colegios c ON c.id_colegios = t3.id_colegio INNER JOIN municipios mu ON mu.id_municipios = c.id_municipios WHERE t3.id_instructor = i.id_instructor) AS municipios, (SELECT GROUP_CONCAT(DISTINCT c2.nombre ORDER BY c2.nombre SEPARATOR '|') FROM tecnicos t4 INNER JOIN colegios c2 ON c2.id_colegios = t4.id_colegio WHERE t4.id_instructor = i.id_instructor) AS colegios FROM instructor i INNER JOIN profesiones p ON p.id_profesion = i.id_profesion WHERE i.activo = 1" 
   
    query2 = "SELECT 'area' AS tipo, id_modalidad AS id, nombre AS nombre FROM modalidad UNION ALL SELECT 'municipio' AS tipo, id_municipios AS id, nombre AS nombre FROM municipios WHERE activo = 1 UNION ALL SELECT 'colegio' AS tipo, id_colegios AS id, nombre AS nombre FROM colegios WHERE activo = 1 ORDER BY tipo, nombre"

    instructores = consulta(query)
    areas = consulta(query2)
    return render_template('instructores.html', instructores = instructores, areas = areas)
@main_bp.route('/instructor/<int:id>')
def instructor(id):

    query = '''
        SELECT
            i.id_instructor AS id,
            i.nombres AS nombre,
            i.apellidos AS apellido,
            i.perfi_profesional AS perfil,
            p.nombre_profesion AS profesion,
            i.foto AS foto
        FROM instructor i
        INNER JOIN profesiones p
            ON i.id_profesion = p.id_profesion
        WHERE i.id_instructor = %s
    '''

    query_colegios = '''
        SELECT
            c.id_colegios AS id,
            c.nombre AS nombre,
            c.logo AS logo,
            m.nombre AS municipio
        FROM tecnicos t
        INNER JOIN colegios c
            ON t.id_colegio = c.id_colegios
        INNER JOIN municipios m
            ON c.id_municipios = m.id_municipios
        WHERE t.id_instructor = %s
          AND c.activo = 1
    '''

    colegios = consulta(query_colegios, (id,))

    query_proyectos = '''
        SELECT
            p.id_proyectos AS id,
            p.nombre AS nombre,
            p.descripcion_corta AS descripcion,
            p.foto_principal AS imagen
        FROM proyectos p
        INNER JOIN tecnicos t
            ON p.id_tecnico = t.id_tecnicos
        WHERE t.id_instructor = %s
          AND p.activo = 1
        ORDER BY p.fecha_registro DESC
    '''

    proyectos = consulta(query_proyectos, (id,))

    resultado = consulta(query, (id,))

    if not resultado:
        return "Instructor no encontrado", 404

    instructor = resultado[0]

    return render_template(
        'instructor.html',
        instructor=instructor,
        colegios=colegios,
        proyectos=proyectos
    )
