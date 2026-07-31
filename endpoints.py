from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import psycopg2 
from tabulate import tabulate

app = FastAPI()

config_db = {
       "dbname": "hola",
       "user": "postgres",
       "password": "Ballenita1.P",
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
    return tabulate(ubicaciones,headers=headers)


@app.get("/analytics/zones/{tipo}")
def zona(tipo):
    conexion = psycopg2.connect(**config_db)
    cursor = conexion.cursor()
    sql_code = """select * from get_zone_summary(%s)"""
    parametros = tipo
    cursor.execute(sql_code,parametros)
    
     