from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from consultas import consulta,insertar



main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def inicio():
    # Los proyectos se consultan con la información del técnico, colegio y modalidad.
    # Se mantiene el resto de la página intacto.
    query1 = """
        SELECT
            p.id_proyectos AS id,
            p.nombre,
            p.descripcion_corta AS descripcion,
            p.descripcion_larga,
            p.objetivo,
            p.resultado,
            p.foto_principal AS foto,
            p.video_intro,
            p.fecha_inicio,
            p.fecha_fin,
            p.activo,
            t.nombre AS tecnico,
            t.ficha,
            c.nombre AS colegio,
            m.nombre AS municipio,
            mo.nombre AS modalidad
        FROM proyectos p
        INNER JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        INNER JOIN colegios c ON c.id_colegios = t.id_colegio
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
        INNER JOIN modalidad mo ON mo.id_modalidad = t.id_modalidad
        WHERE p.activo = 1
        ORDER BY p.nombre ASC
    """
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios WHERE activo = 1"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios WHERE activo = 1"
    query4 = "SELECT id_instructor AS id, nombres, apellidos, id_profesion, foto FROM instructor WHERE activo = 1"
    proyectos = consulta(query1)
    colegios = consulta(query2)
    municipios = consulta(query3)
    instructores = consulta(query4)
    return render_template(
        'index.html',
        proyectos=proyectos,
        colegios=colegios,
        municipios=municipios,
        instructores=instructores
    )


@main_bp.route('/proyecto/<int:id>')
def proyecto(id):
    query = """
        SELECT
            p.*,
            t.nombre AS tecnico,
            t.ficha,
            t.foto_principal AS tecnico_foto,
            c.nombre AS colegio,
            c.logo AS colegio_logo,
            m.nombre AS municipio,
            mo.nombre AS modalidad
        FROM proyectos p
        INNER JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        INNER JOIN colegios c ON c.id_colegios = t.id_colegio
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
        INNER JOIN modalidad mo ON mo.id_modalidad = t.id_modalidad
        WHERE p.id_proyectos = %s AND p.activo = 1
        LIMIT 1
    """
    resultado = consulta(query, (id,))
    if not resultado:
        return render_template('proyectos.html', proyecto=None, galeria=[], videos=[], aprendices=[]), 404

    proyecto = resultado[0]

    galeria = consulta("""
        SELECT id_galeria, url_imagen, descripcion, orden
        FROM proyecto_galeria
        WHERE id_proyecto = %s
        ORDER BY orden ASC, id_galeria ASC
    """, (id,))

    videos = consulta("""
        SELECT id_video, url_video, titulo, orden
        FROM proyecto_videos
        WHERE id_proyecto = %s
        ORDER BY orden ASC, id_video ASC
    """, (id,))

    aprendices = consulta("""
        SELECT a.id_aprendices AS id, a.nombres, a.apellidos, a.foto
        FROM proyecto_aprendices pa
        INNER JOIN aprendices a ON a.id_aprendices = pa.id_aprendiz
        WHERE pa.id_proyecto = %s AND a.activo = 1
        ORDER BY a.apellidos ASC, a.nombres ASC
    """, (id,))

    return render_template(
        'proyectos.html',
        proyecto=proyecto,
        galeria=galeria,
        videos=videos,
        aprendices=aprendices
    )

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



