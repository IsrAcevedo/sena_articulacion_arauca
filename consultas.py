from coneccionbd import obtener_conexion


def consulta(consulta, parametros=None):
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No fue posible conectar con la base de datos.")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(consulta, parametros or ())
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def insertar(consulta, parametros=None):
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No fue posible conectar con la base de datos.")

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(consulta, parametros or ())
        conexion.commit()
        return 'Datos guardados correctamente.'
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def obtener_proyectos():
    conexion = obtener_conexion()
    if conexion is None:
        raise ConnectionError("No fue posible conectar con la base de datos.")

    cursor = None
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
        WHERE p.activo = 1
        ORDER BY p.id_proyectos DESC
    """

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()
