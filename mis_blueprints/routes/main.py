from flask import Flask, abort, render_template, session, url_for, redirect, flash, request, Blueprint
from consultas import consulta,insertar



main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def inicio():
    query1 = "SELECT id_proyectos AS id, nombre, descripcion_corta AS descripcion, foto_principal AS foto FROM proyectos WHERE activo = 1 ORDER BY fecha_inicio DESC LIMIT 3"
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios limit 3"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios WHERE activo = 1"
    query4 = "SELECT i.id_instructor AS id, i.nombres, i.apellidos, p.nombre_profesion as profesion, i.foto FROM instructor i INNER JOIN profesiones p ON i.id_profesion=p.id_profesion limit 4"
    proyectos = consulta(query1)
    colegios = consulta(query2)
    municipios = consulta(query3)
    instructores = consulta(query4)
    return render_template('index.html', proyectos = proyectos, colegios = colegios, municipios = municipios , instructores = instructores)



# Ruta para la página con la lista de proyectos.
@main_bp.route('/proyectos')
def proyectos():
    query = """
        SELECT p.id_proyectos AS id, p.nombre,
               p.descripcion_corta AS descripcion,
               p.foto_principal AS foto,
               t.nombre AS tecnico, c.nombre AS colegio,
               mo.nombre AS modalidad
        FROM proyectos p
        LEFT JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        LEFT JOIN colegios c ON c.id_colegios = t.id_colegio
        LEFT JOIN modalidad mo ON mo.id_modalidad = t.id_modalidad
        WHERE p.activo = 1
        ORDER BY p.fecha_inicio DESC, p.nombre ASC
    """
    proyectos = consulta(query)
    return render_template('proyectos.html', proyectos=proyectos)


@main_bp.route('/proyectos/<int:id>')
@main_bp.route('/proyecto/<int:id>')
def proyecto(id):

    query = """
        SELECT
            p.id_proyectos,
            p.nombre,
            p.descripcion_corta,
            p.descripcion_larga,
            p.objetivo,
            p.resultado,
            p.foto_principal,
            p.video_intro,
            p.fecha_inicio,
            p.fecha_fin,
            t.ficha,
            t.nombre AS tecnico_nombre,
            c.nombre AS colegio_nombre,
            mo.nombre AS modalidad_nombre,
            CONCAT(i.nombres, ' ', i.apellidos) AS instructor_nombre
        FROM proyectos p
        LEFT JOIN tecnicos t
            ON p.id_tecnico = t.id_tecnicos
        LEFT JOIN colegios c
            ON t.id_colegio = c.id_colegios
        LEFT JOIN modalidad mo
            ON t.id_modalidad = mo.id_modalidad
        LEFT JOIN instructor i
            ON t.id_instructor = i.id_instructor
        WHERE p.id_proyectos = %s
          AND p.activo = 1
    """

    proyecto = consulta(query, (id,))

    if not proyecto:
        flash("El proyecto no existe.", "error")
        return redirect(url_for("main.inicio"))

    proyecto = proyecto[0]

    query_aprendices = """
        SELECT a.nombres, a.apellidos
        FROM aprendices a
        INNER JOIN proyecto_aprendices pa
            ON a.id_aprendices = pa.id_aprendiz
        WHERE pa.id_proyecto = %s
          AND a.activo = 1
        ORDER BY a.nombres ASC
    """

    aprendices = consulta(query_aprendices, (id,))

    query_galeria = """
        SELECT url_imagen, descripcion, orden
        FROM proyecto_galeria
        WHERE id_proyecto = %s
        ORDER BY orden ASC
    """

    galeria = consulta(query_galeria, (id,))

    query_videos = """
        SELECT url_video, titulo, orden
        FROM proyecto_videos
        WHERE id_proyecto = %s
        ORDER BY orden ASC
    """

    videos = consulta(query_videos, (id,))

    return render_template(
        'proyecto.html',
        proyecto=proyecto,
        aprendices=aprendices,
        galeria=galeria,
        videos=videos
    )


@main_bp.route('/municipio/<int:id>')
def municipio(id):
    query = "SELECT * FROM municipios WHERE id_municipios = %s"
    parametros = id,
    municipio = consulta(query, parametros)
    if not municipio:
        abort(404)
    return render_template('municipios.html', municipio=municipio[0])

@main_bp.route('/colegios')
def colegios():
    query = 'SELECT c.id_colegios AS id, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio FROM colegios c INNER JOIN municipios m ON m.id_municipios = c.id_municipios'
    colegios = consulta(query)
    return render_template('colegios.html', colegios= colegios)


@main_bp.route('/colegio/<int:id>')
def colegio(id):
    query = 'SELECT * FROM colegios WHERE id_colegios= %s'
    parametros = id,
    colegio = consulta(query, parametros)
    if not colegio:
        abort(404)
    return render_template('colegio.html', colegio=colegio[0])


@main_bp.route('/instructores')
def instructores():
    query = 'SELECT i.id_instructor AS id, i.foto, CONCAT(i.nombres," ",i.apellidos)AS nombre, p.nombre_profesion as profesion, m.nombre as municipio, c.nombre as colegio FROM instructor i INNER JOIN profesiones p ON i.id_profesion = p.id_profesion INNER JOIN tecnicos t ON i.id_instructor = t.id_instructor INNER JOIN colegios c ON t.id_colegio = c.id_colegios INNER JOIN municipios m ON c.id_municipios = m.id_municipios WHERE i.activo = 1'
    instructores = consulta(query) 
    return render_template('instructores.html', instructores = instructores)

@main_bp.route('/instructor/<int:id>')
def instructor(id):
    query = 'SELECT * FROM instructor WHERE id_instructor = %s'
    parametros = id,
    instructor = consulta(query, parametros)
    if not instructor:
        abort(404)
    return render_template('instructor.html', instructor=instructor[0])



