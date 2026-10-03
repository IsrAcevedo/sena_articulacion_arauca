from flask import Flask,  render_template, session, url_for, redirect, flash, request, Blueprint
from math import ceil
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


@main_bp.route('/colegio/<id>')
def colegio(id):
    query1 = 'SELECT c.id_colegios AS id, c.slogan AS slogan, c.nombre AS colegio, c.logo AS logo, m.nombre AS municipio, t.id_tecnicos as id_tecnico, t.nombre as tecnico FROM tecnicos t INNER JOIN colegios c ON t.id_colegio = c.id_colegios INNER JOIN instructor i ON t.id_instructor = i.id_instructor INNER JOIN municipios m ON c.id_municipios = m.id_municipios AND c.id_colegios = %s'
    parametros = id,
    colegio = consulta(query1, parametros)[0]

    query2 ="SELECT DISTINCT i.id_instructor, CONCAT(i.nombres, ' ', i.apellidos) AS instructor_nombre, i.foto, i.perfi_profesional FROM instructor i inner join tecnicos t on i.id_instructor = t.id_instructor inner join colegios c on t.id_colegio = c.id_colegios WHERE c.id_colegios = %s"
    parametros = id,
    instructores = consulta(query2, parametros)

    query3 = "SELECT t.nombre as tecnico, t.id_tecnicos as id_tecnico, t.foto_principal as fotoTecnico FROM tecnicos t INNER JOIN colegios c ON t.id_colegio = c.id_colegios WHERE c.id_colegios = %s"
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


@main_bp.route('/instructores')
def instructores():
    # query = 'SELECT i.id_instructor AS id, i.foto, CONCAT(i.nombres," ",i.apellidos)AS nombre, p.nombre_profesion as profesion, m.nombre as municipio, c.nombre as colegio FROM instructor i INNER JOIN profesiones p ON i.id_profesion = p.id_profesion INNER JOIN tecnicos t ON i.id_instructor = t.id_instructor INNER JOIN colegios c ON t.id_colegio = c.id_colegios INNER JOIN municipios m ON c.id_municipios = m.id_municipios WHERE i.activo = 1'
    # instructores = consulta(query) 
    query = "select i.id_instructor as id, i.foto as foto, CONCAT(i.nombres,' ',i.apellidos) as nombre, p.nombre_profesion as profesion from instructor i inner join profesiones p on p.id_profesion = i.id_profesion" 
    instructores = consulta(query)
    return render_template('instructores.html', instructores = instructores)

@main_bp.route('/instructor/<int:id>')
def instructor(id):
    query = 'SELECT * FROM instructor WHERE id_instructor = %s'
    parametros = id,
    instructor = consulta(query, parametros)[0]
    return render_template('instructor.html', instructor = instructor)



