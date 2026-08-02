from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
import psycopg2 
from tabulate import tabulate
from datetime import date,datetime,timedelta
from pydantic import BaseModel

app = FastAPI()

config_db = {
       "dbname": "hola",
       "user": "postgres",
       "password": "Ballenita1.P",
       "host": "localhost",
       "port": 5432
}

class Ubicacion(BaseModel):
    nombre: str
    piso: str
    tipo_zona: str 
    latitude: float
    longitud: float

@app.get("/ubicacion",response_class=PlainTextResponse)
def mostrar():
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    headers = ["Nombre","Nivel","Tipo de zona"]
    sql_code = """Select * from location"""
    cursor.execute(sql_code)
    ubicaciones = []
    for linea in cursor.fetchall():
        ubicacion = [linea[1], linea[2], linea[3]]
        ubicaciones.append(ubicacion)
        
    cursor.close()
    conexion.close()
    
    return tabulate(eventos,headers=headers)

@app.post("/ubicacion",response_class=PlainTextResponse)
def crear(datos: Ubicacion):
    try:
        conexion = psycopg2.connect(**config_db)
        with conexion:
            with conexion.cursor() as cursor:
                sql_evento = """INSERT INTO "location" ("name", floor, zone_type, latitude, longitude) VALUES (%s, %s, %s, %s, %s) RETURNING UID;"""
                parametros = (datos.nombre,datos.piso,datos.tipo_zona,datos.latitude,datos.longitud)
                cursor.execute(sql_evento,parametros)
    except psycopg2.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {error.pgerror or str(error)}")
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(error)}"
        )
    finally:
        if conexion:
            conexion.close()

@app.get("/camaras",response_class=PlainTextResponse)
def mostrar():
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    headers = ["CID","Nombre","Modelo","Vision Nocturna","Estado"]
    sql_code = """Select * from camera"""
    cursor.execute(sql_code)
    camaras = []
    for linea in cursor.fetchall():
        camara = [linea[0],linea[2], linea[3], linea[4],linea[5]]
        camaras.append(camara)
        
    cursor.close()
    conexion.close()
    
    return tabulate(camaras,headers=headers)

@app.get("/eventos",response_class=PlainTextResponse)
def mostrar():
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    headers = ["EID","Hora","Nivel de confianza"]
    sql_code = """Select * from event"""
    cursor.execute(sql_code)
    eventos = []
    for linea in cursor.fetchall():
        evento = [linea[0], linea[2], linea[3]]
        eventos.append(evento)
        
    cursor.close()
    conexion.close()  
        
    return tabulate(eventos,headers=headers)


@app.get("/analytics/zones/{tipo}",response_class=PlainTextResponse)
def zona(tipo):
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    sql_code = """Select zone_type from "location" """
    cursor.execute(sql_code)
    if (tipo in [zona[0] for zona in cursor.fetchall()]):
        sql_code = """select * from get_zone_summary(%s)"""
        headers = ["Nombre","Num_camaras","Num_eventos","Alertas criticas"]
        cursor.execute(sql_code,(str(tipo),))
        datos = [[f"{dato[0]}",f"{dato[1]}",f"{dato[2]}",f"{dato[3]}"] for dato in cursor.fetchall()]
        
        cursor.close()
        conexion.close()
    
        return(tabulate(datos,headers=headers))
    else: 
        
        cursor.close()
        conexion.close()
        
        return("La zona solicitada no existe")
        
@app.get("/analytics/cameras/{id}/traffic",response_class=PlainTextResponse)
def trafico(id,desde,hasta):
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    desde = date.fromisoformat(str(desde))
    hasta = date.fromisoformat(str(hasta))
    sql_code = """Select * from get_camera_traffic(%s,%s,%s)"""
    cursor.execute(sql_code,(id,desde,hasta))
    headers = ["Total","Hora(en formato militar)"]
    datos= [[f"{dato[0]}",f"{dato[1]}"] for dato in cursor.fetchall()]
    
    cursor.close()
    conexion.close()
    
    return(tabulate(datos,headers=headers))


@app.get("/analytics/alerts/summary",response_class=PlainTextResponse)
def mostrar(days:int):
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    fecha = (datetime.now() - timedelta(days=days),)
    sql_code = """
                  Select c.CID,c.name,c.model,c.has_night_vision,c.state,count(a.severity) filter (where a.severity='critica') as alertas_criticas,count(a.severity) filter (where a.severity='alta') as alertas_altas,count(a.severity) filter (where a.severity='media') as alertas_medias,count(a.severity) filter (where a.severity='baja') as alertas_bajas 
                  from camera as c 
                  left join event as e on e.CID=c.CID
                  left join alert as a on a.EID=e.EID AND a.Atime >= %s
                  group by c.CID 
               """
    cursor.execute(sql_code,fecha)
    
    headers = ["CID","Nombre","Modelo","Vision Nocturna","Estado","alertas_criticas","alertas_altas","alertas_medias","alertas_bajas"]
    datos = [[f"{dato[0]}",f"{dato[1]}",f"{dato[2]}",f"{dato[3]}",f"{dato[4]}",f"{dato[5]}",f"{dato[6]}",f"{dato[7]}",f"{dato[8]}"] for dato in cursor.fetchall()]
    
    cursor.close()
    conexion.close()
    
    return(tabulate(datos,headers=headers))