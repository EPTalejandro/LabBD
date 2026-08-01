from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import psycopg2 
from tabulate import tabulate
from datetime import date

app = FastAPI()

config_db = {
       "dbname": "hola",
       "user": "postgres",
       "password": "******",
       "host": "localhost",
       "port": 5432
}

@app.get("/ubicaciones",response_class=PlainTextResponse)
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
    
    return tabulate(ubicaciones,headers=headers)

@app.get("/camaras",response_class=PlainTextResponse)
def mostrar():
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    headers = ["CID","Nombre","Modelo","Vision Nocturna","Estado"]
    sql_code = """Select * from camera"""
    cursor.execute(sql_code)
    ubicaciones = []
    for linea in cursor.fetchall():
        ubicacion = [linea[0],linea[2], linea[3], linea[4],linea[5]]
        ubicaciones.append(ubicacion)
        
    cursor.close()
    conexion.close()
    
    return tabulate(ubicaciones,headers=headers)

@app.get("/eventos",response_class=PlainTextResponse)
def mostrar():
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    headers = ["EID","Hora","Nivel de confianza"]
    sql_code = """Select * from event"""
    cursor.execute(sql_code)
    ubicaciones = []
    for linea in cursor.fetchall():
        ubicacion = [linea[0], linea[2], linea[3]]
        ubicaciones.append(ubicacion)
        
    cursor.close()
    conexion.close()  
        
    return tabulate(ubicaciones,headers=headers)


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
    