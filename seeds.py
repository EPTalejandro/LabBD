import csv
import psycopg2 

def limpia(valor):
    """Limpia espacios en blanco y convierte celdas vacías en None."""
    if valor is None or str(valor).strip() == "":
        return None
    return str(valor).strip()

def main():
    # Configuración de conexión a la base de datos
    config_db = {
        "dbname": "hola",
        "user": "postgres",
        "password": "Ballenita1.P",
        "host": "localhost",
        "port": 5432
    }
    
    # Ruta del archivo CSV 
    ruta_csv = 'seed_100.csv' 
    
    try:
        conexion = psycopg2.connect(**config_db)
        cursor = conexion.cursor()

        # Diccionarios de caché para evitar duplicar entidades estáticas en la BD
        location_cache = {}
        camera_cache = {}

        with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo) 
            
            for fila in lector_csv:
                
                # 1. PROCESAR UBICACIÓN ("location")
                loc_key = (
                    limpia(fila.get('ubicacion_nombre')),
                    limpia(fila.get('ubicacion_piso')),
                    limpia(fila.get('ubicacion_tipo_zona')),
                    limpia(fila.get('ubicacion_latitud')),
                    limpia(fila.get('ubicacion_longitud'))
                )
                
                # Si la combinación de la ubicación no se ha insertado, la registramos
                if loc_key not in location_cache:
                    sql_ubicacion = """
                        INSERT INTO "location" ("name", floor, zone_type, latitude, longitude) 
                        VALUES (%s, %s, %s, %s, %s) 
                        RETURNING UID;
                    """
                    cursor.execute(sql_ubicacion, loc_key)
                    location_cache[loc_key] = cursor.fetchone()[0]
                
                id_ubi = location_cache[loc_key]
                
                # 2. PROCESAR CÁMARA (camera)
                cam_name = limpia(fila.get('camara_nombre'))
                if cam_name and cam_name not in camera_cache:
                    # Convertir el texto de visión nocturna a Booleano de Python
                    vision_nocturna = False
                    vn_str = limpia(fila.get('camara_vision_nocturna'))
                    if vn_str:
                        vision_nocturna = vn_str.lower() in ('true', '1', 't', 'yes')
                        
                    sql_camara = """
                        INSERT INTO camera (UID, "name", model, has_night_vision, "state") 
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING CID;
                    """
                    cursor.execute(sql_camara, (
                        id_ubi, 
                        cam_name, 
                        limpia(fila.get('camara_modelo')), 
                        vision_nocturna, 
                        limpia(fila.get('camara_estado'))
                    ))
                    camera_cache[cam_name] = cursor.fetchone()[0]
                
                id_cam = camera_cache.get(cam_name)
                
                # 3. PROCESAR EVENTO ("event")
                conf_level = limpia(fila.get('evento_confianza'))
                if conf_level is not None:
                    sql_evento = """
                        INSERT INTO "event" (CID, eTime, conf_level, posX, posY, width, height) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING EID;
                    """
                    cursor.execute(sql_evento, (
                        id_cam,
                        limpia(fila.get('evento_marca_tiempo')),
                        conf_level,
                        limpia(fila.get('evento_bbox_x')),
                        limpia(fila.get('evento_bbox_y')),
                        limpia(fila.get('evento_bbox_w')),
                        limpia(fila.get('evento_bbox_h'))
                    ))
                    id_evento = cursor.fetchone()[0]
                else:
                    # Si la fila no contiene datos de un evento válido, saltamos al siguiente registro
                    continue
                
                # 4. PROCESAR ALERTA (alert) - Opcional, solo si existe en la fila
                alerta_sev = limpia(fila.get('alerta_severidad'))
                if alerta_sev is not None:
                    sql_alerta = """
                        INSERT INTO alert (EID, severity, "state", "description") 
                        VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(sql_alerta, (
                        id_evento,
                        alerta_sev,
                        limpia(fila.get('alerta_estado')),
                        limpia(fila.get('alerta_descripcion'))
                    ))
                
                # 5. PROCESAR OBJETO ("object")
                tipo_original = limpia(fila.get('objeto_tipo'))
                if tipo_original is not None:
                    # Mapear valores en español a los exigidos por el CHECK constraint inglés
                    if tipo_original == 'persona':
                        object_type = 'person'
                        color = limpia(fila.get('persona_color_ropa'))
                        luggage = limpia(fila.get('persona_porta_equipaje'))
                        vehicle_type = None
                        license_plate = None
                    elif tipo_original == 'vehiculo':
                        object_type = 'vehicle'
                        color = limpia(fila.get('vehiculo_color'))
                        luggage = None
                        vehicle_type = limpia(fila.get('vehiculo_tipo'))
                        license_plate = limpia(fila.get('vehiculo_matricula'))
                    else:
                        object_type = tipo_original
                        color = None
                        luggage = None
                        vehicle_type = None
                        license_plate = None

                    sql_objeto = """
                        INSERT INTO "object" (EID, object_type, color, luggage, "vehicle", license_plate) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING OID;
                    """
                    cursor.execute(sql_objeto, (
                        id_evento, 
                        object_type, 
                        color, 
                        luggage, 
                        vehicle_type, 
                        license_plate
                    ))
                    id_objeto = cursor.fetchone()[0]
                    
                    # 6. PROCESAR EMBEDDING (embedding) - Opcional
                    embedding_str = limpia(fila.get('objeto_embedding'))
                    if embedding_str is not None:
                        sql_embedding = """
                            INSERT INTO embedding (OID, embedding_vec) 
                            VALUES (%s, %s);
                        """
                        cursor.execute(sql_embedding, (id_objeto, embedding_str))
        
        # Confirmar todas las transacciones de manera segura al final
        conexion.commit()
        print("¡La base de datos ha sido poblada exitosamente sin duplicados!")

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
