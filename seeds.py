import csv
import psycopg2 
def limpia(valor):
    if valor == "":
        return None
    else:
        return valor
def main():
    config_db = {
    "dbname": "hola",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": 5432
    }
    ruta_csv = '/home/alejandro/Materias/Bases de datos/LabBD/seeders.csv'
    try:
        conexion = psycopg2.connect(**config_db)
        cursor = conexion.cursor()

        with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo) 
            
            for fila in lector_csv:
                sql_ubicacion = """
                    INSERT INTO ubicacion (edificio,piso,zonetype,latitud,longitud) 
                    VALUES (%s, %s,%s,%s,%s) 
                    RETURNING UID;
                """
                cursor.execute(sql_ubicacion, (limpia(fila['ubicacion_nombre']), limpia(fila['ubicacion_piso']),limpia(fila['ubicacion_tipo_zona']),limpia(fila['ubicacion_latitud']),limpia(fila['ubicacion_longitud'])))
                id_ubi = cursor.fetchone()[0]
                
                if(fila['camara_nombre'] != ""):      
                    sql_camara = """
                        INSERT INTO camara (nombre,modelo,UID,has_night_vision,estado) 
                        VALUES (%s, %s,%s,%s,%s)
                        RETURNING CID;
                    """
                    cursor.execute(sql_camara, (limpia(fila['camara_nombre']),limpia(fila['camara_modelo']),id_ubi,limpia(fila['camara_vision_nocturna']),limpia(fila['camara_estado'])))
                    id_cam = cursor.fetchone()[0]
                
                if(not(limpia(fila['evento_confianza']) is None)):
                    sql_evento = """
                        INSERT INTO evento (eTiempo, conf_level,posX,posY,CID,ancho,alto) 
                        VALUES (%s, %s,%s,%s,%s,%s,%s)
                        RETURNING EID;
                    """
                    cursor.execute(sql_evento, (limpia(fila['evento_marca_tiempo']),limpia(fila['evento_confianza']),limpia(fila['evento_bbox_x']),limpia(fila['evento_bbox_y']),id_cam,limpia(fila['evento_bbox_w']),limpia(fila['evento_bbox_h'])))
                    id_evento = cursor.fetchone()[0]
                
                if(limpia(fila['alerta_severidad']) is not None):
                    sql_alerta = """
                        INSERT INTO alerta (EID,severidad,estado,descripcion) 
                        VALUES (%s, %s,%s,%s)
                        RETURNING AID;
                    """
                    cursor.execute(sql_alerta, (id_evento,limpia(fila['alerta_severidad']),limpia(fila['alerta_estado']),limpia(fila['alerta_descripcion'])))
                    id_alerta = cursor.fetchone()[0]
                
                color = ""
                
                if fila['objeto_tipo'] == 'persona':
                    color = fila['persona_color_ropa']
                else :
                    color = fila['vehiculo_color']
                if(limpia(fila['objeto_tipo']) is not None):
                    sql_objeto = """
                        INSERT INTO objeto (EID,tipo,color,equipaje,vehiculo,matricula,embedding) 
                        VALUES (%s, %s,%s,%s,%s,%s,%s)
                    """
                    cursor.execute(sql_objeto, (id_evento,limpia(fila['objeto_tipo']),color,limpia(fila['persona_porta_equipaje']),limpia(fila['vehiculo_tipo']),limpia(fila['vehiculo_matricula']),limpia(fila['objeto_embedding'])))
        
        conexion.commit()
        print("¡Datos distribuidos y llaves foráneas enlazadas con éxito!")

    except Exception as error:
        if 'conexion' in locals():
            conexion.rollback()
        print(f"Error durante la importación: {error}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()
            
if __name__ == "__main__":
    main()