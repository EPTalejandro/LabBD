from fastapi import FastAPI, HTTPException, status, Query
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

app = FastAPI()

config_db = {
       "dbname": "hola",
       "user": "postgres",
       "password": "Ballenita1.P",
       "host": "localhost",
       "port": 5432
}

# Conectar con la base de datos
def get_conexion():
    return psycopg2.connect(**config_db)

# Convierte una lista de floats en el literal de texto que pgvector espera, ej. '[0.1,0.2,...]'
def vector_a_literal(vector: List[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


# Modelos Pydantic
# Son para definir estructuras y poder validad los datos automáticamente

class Ubicacion(BaseModel):
    name: str
    floor: str
    zone_type: str
    latitude: float
    longitude: float

class UbicacionUpdate(BaseModel):
    name: Optional[str] = None
    floor: Optional[str] = None
    zone_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Camara(BaseModel):
    UID: UUID
    name: str
    model: str
    has_night_vision: bool = False
    state: str = "activa"

class CamaraUpdate(BaseModel):
    UID: Optional[UUID] = None
    name: Optional[str] = None
    model: Optional[str] = None
    has_night_vision: Optional[bool] = None
    state: Optional[str] = None

class Evento(BaseModel):
    cid: UUID
    conf_level: float
    posx: int
    posy: int
    width: int
    height: int

class BusquedaVector(BaseModel):
    vector: List[float] = Field(..., min_length=512, max_length=512)
    tipo: Optional[str] = None
    limit: int = 10

# Entregable 4A - Endpoints CRUD

# Ubicación

# Modificado
@app.get("/ubicaciones")
def listar_ubicaciones():
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        sql_code = """SELECT UID, name, floor, zone_type, latitude, longitude FROM "location" """
        cursor.execute(sql_code)
        ubicaciones = cursor.fetchall()
        cursor.close()
        return ubicaciones      # FastAPI lo convierte automáticamente a JSON
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

#
@app.post("/ubicaciones", status_code=status.HTTP_201_CREATED)
def crear_ubicacion(datos: Ubicacion):
    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor(cursor_factory = RealDictCursor) as cursor:
                sql_code = """
                    INSERT INTO "location" (name, floor, zone_type, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING uid, name, floor, zone_type, latitude, longitude;
                """
                parametros = (datos.name, datos.floor, datos.zone_type, datos.latitude, datos.longitude)
                cursor.execute(sql_code, parametros)
                fila = cursor.fetchone()
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

# 
@app.put("/ubicaciones/{id}")
def actualizar_ubicacion(id: UUID, datos: UbicacionUpdate):
    campos = {
        "name": datos.name,
        "floor": datos.floor,
        "zone_type": datos.zone_type,
        "latitude": datos.latitude,
        "longitude": datos.longitude,
    }
    campos = {columna: valor for columna, valor in campos.items() if valor is not None}
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron campos para actualizar")

    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor(cursor_factory = RealDictCursor) as cursor:
                set_clause = ", ".join(f"{columna} = %s" for columna in campos)
                sql_code = f"""
                    UPDATE "location" SET {set_clause}
                    WHERE uid = %s
                    RETURNING uid, name, floor, zone_type, latitude, longitude;
                """
                parametros = list(campos.values()) + [str(id)]
                cursor.execute(sql_code, parametros)
                fila = cursor.fetchone()
                if fila is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


@app.delete("/ubicaciones/{id}")
def eliminar_ubicacion(id: UUID):
    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor() as cursor:
                sql_code = """DELETE FROM "location" WHERE uid = %s RETURNING uid;"""
                cursor.execute(sql_code, (str(id),))
                fila = cursor.fetchone()
                if fila is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicacion no encontrada")
        return {"detalle": "Ubicacion eliminada", "uid": fila[0]}
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

# Camaras

# Modificado
@app.get("/camaras")
def listar_camaras():
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        sql_code = """SELECT CID, UID, name, model, has_night_vision, state FROM camera"""
        cursor.execute(sql_code)
        camaras = cursor.fetchall()
        cursor.close()
        return camaras
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

#
@app.get("/camaras/{id}")
def obtener_camara(id: UUID):
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        sql_code = """SELECT cid, uid, name, model, has_night_vision, state FROM camera WHERE cid = %s"""
        cursor.execute(sql_code, (str(id),))
        fila = cursor.fetchone()
        cursor.close()
        if fila is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camara no encontrada")
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

#
@app.post("/camaras", status_code=status.HTTP_201_CREATED)
def crear_camara(datos: Camara):
    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor(cursor_factory = RealDictCursor) as cursor:
                sql_code = """
                    INSERT INTO camera (uid, name, model, has_night_vision, state)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING cid, uid, name, model, has_night_vision, state;
                """
                parametros = (str(datos.UID), datos.name, datos.model, datos.has_night_vision, datos.state)
                cursor.execute(sql_code, parametros)
                fila = cursor.fetchone()
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


@app.put("/camaras/{id}")
def actualizar_camara(id: UUID, datos: CamaraUpdate):
    campos = {
        "UID": str(datos.UID) if datos.UID else None,
        "name": datos.name,
        "model": datos.model,
        "has_night_vision": datos.has_night_vision,
        "state": datos.state,
    }
    campos = {columna: valor for columna, valor in campos.items() if valor is not None}
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron campos para actualizar")

    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor(cursor_factory = RealDictCursor) as cursor:
                set_clause = ", ".join(f"{columna} = %s" for columna in campos)
                sql_code = f"""
                    UPDATE camera SET {set_clause}
                    WHERE cid = %s
                    RETURNING cid, uid, name, model, has_night_vision, state;
                """
                parametros = list(campos.values()) + [str(id)]
                cursor.execute(sql_code, parametros)
                fila = cursor.fetchone()
                if fila is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camara no encontrada")
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

# Eventos

# Modificado
@app.get("/eventos")
def listar_eventos():
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        sql_code = """SELECT EID, CID, etime, conf_level, posx, posy, width, height FROM "event" """
        cursor.execute(sql_code)
        eventos = cursor.fetchall()
        cursor.close()
        return eventos
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


@app.post("/eventos", status_code=status.HTTP_201_CREATED)
def crear_evento(datos: Evento):
    conexion = None
    try:
        conexion = get_conexion()
        with conexion:
            with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
                sql_code = """
                    INSERT INTO "event" (cid, conf_level, posx, posy, width, height)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING eid, cid, etime, conf_level, posx, posy, width, height;
                """
                parametros = (str(datos.cid), datos.conf_level, datos.posx, datos.posy, datos.width, datos.height)
                cursor.execute(sql_code, parametros)
                fila = cursor.fetchone()
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


@app.get("/eventos/{id}")
def obtener_evento(id: UUID):
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        sql_code = """SELECT eid, cid, etime, conf_level, posx, posy, width, height FROM "event" WHERE eid = %s"""
        cursor.execute(sql_code, (str(id),))
        fila = cursor.fetchone()
        cursor.close()
        if fila is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
        return fila
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()



# Entregable 4B - Endpoints analiticos

# Modificado
@app.get("/analytics/zones/{tipo}")
def resumen_zona(tipo: str):
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        sql_code = """SELECT DISTINCT zone_type FROM "location" """
        cursor.execute(sql_code)
        tipos_validos = [fila[0] for fila in cursor.fetchall()]
        if tipo not in tipos_validos:
            cursor.close()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La zona '{tipo}' no existe")

        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        sql_code = """SELECT * FROM get_zone_summary(%s)"""
        cursor.execute(sql_code, (tipo,))
        datos = cursor.fetchall()
        cursor.close()
        return datos
    
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

# Modificado
@app.get("/analytics/cameras/{id}/traffic")
def trafico_camara(id: UUID, desde: date = Query(..., alias="from"), hasta: date = Query(..., alias="to")):
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        sql_code = """SELECT * FROM get_camera_traffic(%s, %s, %s)"""
        cursor.execute(sql_code, (str(id), desde, hasta))
        datos = cursor.fetchall()
        cursor.close()
        return datos
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()

# Modificado
@app.get("/analytics/alerts/summary")
def resumen_alertas(days: int = 30):
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        fecha_limite = datetime.now() - timedelta(days=days)
        sql_code = """
            SELECT
                c.CID, c.name, c.model, c.has_night_vision, c.state,
                count(a.severity) FILTER (WHERE a.severity = 'critica') AS alertas_criticas,
                count(a.severity) FILTER (WHERE a.severity = 'alta')    AS alertas_altas,
                count(a.severity) FILTER (WHERE a.severity = 'media')   AS alertas_medias,
                count(a.severity) FILTER (WHERE a.severity = 'baja')    AS alertas_bajas
            FROM camera AS c
            LEFT JOIN "event" AS e ON e.cid = c.cid
            LEFT JOIN alert AS a ON a.eid = e.eid AND a.atime >= %s
            GROUP BY c.cid
        """
        cursor.execute(sql_code, (fecha_limite,))
        datos = cursor.fetchall()
        cursor.close()
        return datos
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


# Entregable 4C - Endpoints vectoriales

@app.get("/objects/{id}/similar")
def objetos_similares(id: UUID, threshold: float = 0.20, limit: int = 5):
    """
    Retorna los objetos visualmente similares al objeto indicado, invocando
    find_similar_objects(ref_id UUID, threshold FLOAT, max_results INT),
    que retorna: object_id, object_type, distancia_coseno, camera_name, tiempo.
    Ya excluye al propio objeto de referencia y filtra por el mismo object_type.
    """
    conexion = None
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()

        cursor.execute("""SELECT 1 FROM "object" WHERE oid = %s""", (str(id),))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objeto no encontrado")

        sql_code = """SELECT object_id, object_type, distancia_coseno, camera_name, tiempo
                       FROM find_similar_objects(%s, %s, %s)"""
        cursor.execute(sql_code, (str(id), threshold, limit))
        resultados = [
            {
                "object_id": fila[0],
                "object_type": fila[1],
                "distancia_coseno": fila[2],
                "camera_name": fila[3],
                "tiempo": fila[4],
            }
            for fila in cursor.fetchall()
        ]
        cursor.close()
        return {"object_id": str(id), "threshold": threshold, "limit": limit, "resultados": resultados}
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()


@app.post("/search/similar")
def buscar_por_vector(datos: BusquedaVector):
    """
    Recibe un embedding de 512 dimensiones y retorna los objetos registrados
    con menor distancia coseno a ese vector.
    """
    conexion = None
    try:
        vector_literal = vector_a_literal(datos.vector)
        conexion = get_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        where_clause = ""
        parametros = [vector_literal]

        if datos.tipo is not None:
            where_clause = "WHERE o.object_type = %s"
            parametros.append(datos.tipo)

        sql_code = f"""
            SELECT
                o.oid, o.object_type, o.color, o.luggage, o.vehicle, o.license_plate,
                e.eid, e.etime, c.cid, c.name AS camera_name,
                (em.embedding_vec <=> %s::vector) AS distancia
            FROM embedding em
            JOIN "object" o ON o.oid = em.oid
            JOIN "event" e ON e.eid = o.eid
            JOIN camera c ON c.cid = e.cid
            {where_clause}
            ORDER BY em.embedding_vec <=> %s::vector
            LIMIT %s
        """
        parametros.extend([vector_literal, datos.limit])

        cursor.execute(sql_code, parametros)
        resultados = cursor.fetchall()
        cursor.close()
        return {"limit": datos.limit, "tipo": datos.tipo, "resultados": resultados}
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    finally:
        if conexion:
            conexion.close()
