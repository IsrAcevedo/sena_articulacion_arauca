from coneccionbd import obtener_conexion


def consulta(consulta, parametros=None):
    conexion = obtener_conexion()
    cursor= conexion.cursor(dictionary=True)
    cursor.execute(consulta, parametros or ())
    resultado = cursor.fetchall()
    conexion.close()
    return resultado
    
def insertar(consulta, parametros=None):
    conexion=obtener_conexion()
    cursor=conexion.cursor()
    cursor.execute(consulta,parametros or())
    conexion.commit()
    cursor.close()
    conexion.close()
    return 'datos insertados correctamente'
        