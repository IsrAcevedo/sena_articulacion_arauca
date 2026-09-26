from coneccionbd import obtener_conexion


def consulta(consulta, parametros=None):

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    cursor.execute(consulta, parametros or ())

    resultado = cursor.fetchall()

    conexion.close()

    return resultado


def insertar(consulta, parametros=None):

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(consulta, parametros or ())

    conexion.commit()

    cursor.close()

    conexion.close()

    return 'datos insertados correctamente'


def obtener_proyectos():

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

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

    cursor.execute(query)

    proyectos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return proyectos