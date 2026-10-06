from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from math import ceil
from consultas import consulta,insertar



main_bp = Blueprint('main', __name__)

#ruta para la pagina principal

@main_bp.route('/')
def inicio():
    query1 = "SELECT id_proyectos AS id, nombre, descripcion_corta AS descripcion, foto_principal AS foto FROM proyectos limit 3"
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios WHERE activo = 1 AND es_destacado = 1 limit 3"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios WHERE activo = 1"
    query4 = "SELECT i.id_instructor AS id, i.nombres, i.apellidos, p.nombre_profesion as profesion, i.foto FROM instructor i INNER JOIN profesiones p ON i.id_profesion=p.id_profesion limit 4"
    proyectos = consulta(query1)
    colegios = consulta(query2)
    municipios = consulta(query3)
    instructores = consulta(query4)
    return render_template('index.html', proyectos = proyectos, colegios = colegios, municipios = municipios , instructores = instructores)


#ruta para la pagina con lista de proyectos
@main_bp.route('/proyectos')
def proyectos():
    query = "SELECT id_proyectos AS id, nombre, descripcion_corta AS descripcion, foto_principal AS foto FROM proyectos"
    proyectos = consulta(query)
    return render_template('proyectos.html', proyectos=proyectos)


#ruta para la pagina con detalle de proyecto
@main_bp.route('/proyectos/<int:id>')
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
        INNER JOIN tecnicos t
            ON p.id_tecnico = t.id_tecnicos
        INNER JOIN colegios c
            ON t.id_colegio = c.id_colegios
        INNER JOIN modalidad mo
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

    # APRENDICES DEL PROYECTO
    query_aprendices = """
        SELECT
            a.nombres,
            a.apellidos
        FROM aprendices a
        INNER JOIN proyecto_aprendices pa
            ON a.id_aprendices = pa.id_aprendiz
        WHERE pa.id_proyecto = %s
          AND a.activo = 1
        ORDER BY a.nombres ASC
    """

    aprendices = consulta(query_aprendices, (id,))

    # GALERÍA DEL PROYECTO
    query_galeria = """
        SELECT
            url_imagen,
            descripcion,
            orden
        FROM proyecto_galeria
        WHERE id_proyecto = %s
        ORDER BY orden ASC
    """

    galeria = consulta(query_galeria, (id,))

    # VIDEOS DEL PROYECTO
    query_videos = """
        SELECT
            url_video,
            titulo,
            orden
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


#ruta para la pagina con lista de municipios
@main_bp.route('/municipios')
def municipios():
    # Municipios activos
    query = "SELECT * FROM municipios WHERE activo = 1 ORDER BY nombre"
    municipios = consulta(query)

    total_municipios = len(municipios) if municipios else 0

    # Colegios
    query_colegios = "SELECT COUNT(*) as total FROM colegios WHERE activo = 1"
    total_colegios = consulta(query_colegios)[0]['total']

    # Proyectos
    query_proyectos = "SELECT COUNT(*) as total FROM proyectos WHERE activo = 1"
    total_proyectos = consulta(query_proyectos)[0]['total']

    # Instructores (la tabla se llama "instructor")
    query_instructores = "SELECT COUNT(*) as total FROM instructor WHERE activo = 1"
    total_instructores = consulta(query_instructores)[0]['total']

    return render_template(
        'municipios.html',
        municipios=municipios,
        total_municipios=total_municipios,
        total_colegios=total_colegios,
        total_proyectos=total_proyectos,
        total_instructores=total_instructores
    )


@main_bp.route('/municipio/<int:id>')
def municipio(id):
    query = "SELECT * FROM municipios WHERE id_municipios = %s AND activo = 1"
    resultado = consulta(query, (id,))

    if not resultado:
        abort(404)

    municipio = resultado[0] if isinstance(resultado, list) else resultado

    # Solo podemos contar colegios de forma real (tiene id_municipios)
    query_colegios = "SELECT COUNT(*) as total FROM colegios WHERE id_municipios = %s AND activo = 1"
    num_colegios = consulta(query_colegios, (id,))[0]['total']

    # Proyectos e instructores todavía no tienen relación directa con municipio
    num_proyectos = 0
    num_instructores = 0

    return render_template(
        'municipio.html',
        municipio=municipio,
        num_colegios=num_colegios,
        num_proyectos=num_proyectos,
        num_instructores=num_instructores
    )

#ruta para la pagina con lista de colegios
@main_bp.route('/colegios')
def colegios():
    # 1. Leer lo que viene en la URL (?q=...&pagina=...)
    busqueda = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 4  # tarjetas por página

    # 2. Tu consulta de siempre
    query = 'SELECT c.id_colegios AS id,c.slogan AS slogan, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio FROM municipios m INNER JOIN colegios c ON m.id_municipios = c.id_municipios '
    todos = consulta(query)

    # 3. Buscador: dejar solo los que contengan el texto buscado
    if busqueda:
        texto = busqueda.lower()
        todos = [
            c for c in todos
            if texto in (c['colegio'] or '').lower()
            or texto in (c['municipio'] or '').lower()
        ]

    # 4. Paginador: calcular cuántas páginas hay y cortar la lista
    total = len(todos)
    total_paginas = max(ceil(total / por_pagina), 1)
    pagina = min(max(pagina, 1), total_paginas)  # evita páginas inválidas

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    colegios_pagina = todos[inicio:fin]

    return render_template(
        'colegios.html',
        colegios=colegios_pagina,
        busqueda=busqueda,
        pagina=pagina,
        total_paginas=total_paginas,
        total=total
    )

#ruta para la pagina con detalle de colegio
@main_bp.route('/colegio/<id>')
def colegio(id):
    query1 = 'SELECT c.id_colegios AS id, c.slogan AS slogan, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio, t.id_tecnicos as id_tecnico, t.nombre as tecnico FROM tecnicos t INNER JOIN colegios c ON t.id_colegio = c.id_colegios INNER JOIN instructor i ON t.id_instructor = i.id_instructor INNER JOIN municipios m ON c.id_municipios = m.id_municipios AND c.id_colegios = %s'
    parametros = id,
    colegio = consulta(query1, parametros)[0]

    query2 ="SELECT DISTINCT i.id_instructor, CONCAT(i.nombres, ' ', i.apellidos) AS instructor_nombre, i.foto, i.perfi_profesional FROM instructor i inner join tecnicos t on i.id_instructor = t.id_instructor inner join colegios c on t.id_colegio = c.id_colegios WHERE c.id_colegios = %s"
    parametros = id,
    instructores = consulta(query2, parametros)

    query3 = "SELECT t.nombre as tecnico, t.ficha as ficha, t.id_tecnicos as id_tecnico, t.foto_principal as fotoTecnico, mo.nombre as modalidad FROM tecnicos t INNER JOIN colegios c ON t.id_colegio = c.id_colegios INNER JOIN modalidad mo ON t.id_modalidad = mo.id_modalidad WHERE c.id_colegios = %s"
    parametros = id,
    tecnicos = consulta(query3, parametros)

    query4 = "SELECT p.id_proyectos as id, p.nombre as proyecto, p.descripcion_corta as descripcion, p.foto_principal as foto, p.activo FROM tecnicos t INNER JOIN proyectos p ON t.id_tecnicos = p.id_tecnico INNER JOIN colegios c ON t.id_colegio = c.id_colegios WHERE c.id_colegios = %s"
    parametros = id,
    proyectos = consulta(query4, parametros)

    query_estudiantes = """SELECT a.id_aprendices, a.nombres, a.apellidos, a.numero_identificacion, 
        a.foto, a.activo, a.id_tecnico FROM aprendices a 
        INNER JOIN tecnicos t ON a.id_tecnico = t.id_tecnicos 
        WHERE t.id_colegio = %s"""
    parametros = id,
    estudiantes = consulta(query_estudiantes, parametros)

    # Conteo de técnicos
    query_count_tecnicos = """SELECT COUNT(*) as total FROM tecnicos t 
        INNER JOIN colegios c ON t.id_colegio = c.id_colegios 
        WHERE c.id_colegios = %s"""
    parametros = id,
    total_tecnicos = consulta(query_count_tecnicos, parametros)[0]['total']

    # Conteo de proyectos
    query_count_proyectos = """SELECT COUNT(*) as total FROM tecnicos t 
        INNER JOIN proyectos p ON t.id_tecnicos = p.id_tecnico 
        INNER JOIN colegios c ON t.id_colegio = c.id_colegios 
        WHERE c.id_colegios = %s"""
    parametros = id,
    total_proyectos = consulta(query_count_proyectos, parametros)[0]['total']

    query_count_instructores = """SELECT COUNT(DISTINCT i.id_instructor) as total 
    FROM instructor i INNER JOIN tecnicos t ON i.id_instructor = t.id_instructor 
    INNER JOIN colegios c ON t.id_colegio = c.id_colegios 
    WHERE c.id_colegios = %s"""
    parametros = id,
    total_instructores = consulta(query_count_instructores, parametros)[0]['total']

    return render_template('colegio.html', colegio=colegio, instructores=instructores, 
    tecnicos=tecnicos, proyectos=proyectos,
    estudiantes=estudiantes, total_tecnicos=total_tecnicos, total_instructores=total_instructores, total_proyectos=total_proyectos)

#ruta para la pagina con lista de instructores
@main_bp.route('/instructores')
def instructores():
    query = "SELECT i.id_instructor AS id, i.foto AS foto, CONCAT(i.nombres, ' ', i.apellidos) AS nombre, p.nombre_profesion AS profesion, (SELECT GROUP_CONCAT(DISTINCT t.id_modalidad ORDER BY t.id_modalidad SEPARATOR ',') FROM tecnicos t WHERE t.id_instructor = i.id_instructor) AS areas_ids, (SELECT GROUP_CONCAT(DISTINCT m.nombre ORDER BY m.nombre SEPARATOR '|') FROM tecnicos t2 INNER JOIN modalidad m ON m.id_modalidad = t2.id_modalidad WHERE t2.id_instructor = i.id_instructor) AS areas_nombres, (SELECT GROUP_CONCAT(DISTINCT mu.nombre ORDER BY mu.nombre SEPARATOR '|') FROM tecnicos t3 INNER JOIN colegios c ON c.id_colegios = t3.id_colegio INNER JOIN municipios mu ON mu.id_municipios = c.id_municipios WHERE t3.id_instructor = i.id_instructor) AS municipios, (SELECT GROUP_CONCAT(DISTINCT c2.nombre ORDER BY c2.nombre SEPARATOR '|') FROM tecnicos t4 INNER JOIN colegios c2 ON c2.id_colegios = t4.id_colegio WHERE t4.id_instructor = i.id_instructor) AS colegios FROM instructor i INNER JOIN profesiones p ON p.id_profesion = i.id_profesion WHERE i.activo = 1" 
   
    query2 = "SELECT 'area' AS tipo, id_modalidad AS id, nombre AS nombre FROM modalidad UNION ALL SELECT 'municipio' AS tipo, id_municipios AS id, nombre AS nombre FROM municipios WHERE activo = 1 UNION ALL SELECT 'colegio' AS tipo, id_colegios AS id, nombre AS nombre FROM colegios WHERE activo = 1 ORDER BY tipo, nombre"

    instructores = consulta(query)
    areas = consulta(query2)
    return render_template('instructores.html', instructores = instructores, areas = areas)

#ruta para la pagina con detalle de instructor    
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
