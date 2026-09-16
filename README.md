# SecureVision C.A. — API de Videovigilancia Inteligente

API RESTful desarrollada con FastAPI y PostgreSQL (con la extensión `pgvector`) para la gestión y analítica de un sistema de videovigilancia: ubicaciones, cámaras, eventos, alertas y búsqueda de objetos por similitud visual.

Este README cubre cómo levantar el proyecto localmente y cómo probar cada grupo de endpoints. Para la explicación de la lógica interna y las decisiones de diseño, ver el informe (Entregable 4D).

## Requisitos previos

- Python 3.10 o superior
- PostgreSQL 14 o superior, con la extensión `pgvector` instalada
- El esquema de la base de datos ya creado (tablas `location`, `camera`, `event`, `object`, `embedding`, `alert`) junto con las funciones PL/pgSQL de la Fase 3 (`get_zone_summary`, `get_camera_traffic`, `find_similar_objects`)

## Instalación

Clona el repositorio y crea un entorno virtual:

```bash
git clone <url-del-repositorio>
cd <carpeta-del-repositorio>
python3 -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

El proyecto lee la configuración de la base de datos desde variables de entorno. Copia el archivo de ejemplo y completa tus propios valores:

```bash
cp .env.example .env
```

Contenido esperado de `.env`:

```
DB_NAME=hola
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

**No subas el archivo `.env` al repositorio** — ya está (o debería estar) listado en `.gitignore`.

## Preparar la base de datos

Antes de levantar la API, asegúrate de que la extensión `pgvector` esté habilitada en tu base:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Luego ejecuta, en este orden, los scripts de las fases anteriores:

```bash
psql -U postgres -d hola -f squema.sql
psql -U postgres -d hola -f funciones.sql
psql -U postgres -d hola -f triggers.sql
```

Si quieres cargar datos de prueba, el repositorio incluye `seed_100.csv` y `seeds.py` para poblar la base.

## Ejecutar el proyecto

Con el entorno virtual activado y el `.env` configurado:

```bash
uvicorn endpoints:app --reload
```

La API queda disponible en `http://localhost:8000`. FastAPI genera documentación interactiva automáticamente en:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Desde `/docs` puedes probar cualquier endpoint directamente desde el navegador sin necesidad de `curl` ni Postman.

## Probar los endpoints

A continuación, ejemplos de uso con `curl` para cada grupo de endpoints. Sustituye los UUID de ejemplo por valores reales de tu base de datos.

### Ubicaciones (4A)

```bash
# Listar todas las ubicaciones
curl http://localhost:8000/ubicaciones

# Crear una ubicación
curl -X POST http://localhost:8000/ubicaciones \
  -H "Content-Type: application/json" \
  -d '{"name": "Entrada principal", "floor": "PB", "zone_type": "acceso", "latitude": 10.4, "longitude": -66.9}'

# Actualizar parcialmente una ubicación
curl -X PUT http://localhost:8000/ubicaciones/<uid> \
  -H "Content-Type: application/json" \
  -d '{"floor": "1"}'

# Eliminar una ubicación
curl -X DELETE http://localhost:8000/ubicaciones/<uid>
```

### Cámaras (4A)

```bash
curl http://localhost:8000/camaras
curl http://localhost:8000/camaras/<cid>

curl -X POST http://localhost:8000/camaras \
  -H "Content-Type: application/json" \
  -d '{"UID": "<uid-de-una-ubicacion>", "name": "Cam-01", "model": "Hikvision X200", "has_night_vision": true, "state": "activa"}'

curl -X PUT http://localhost:8000/camaras/<cid> \
  -H "Content-Type: application/json" \
  -d '{"state": "mantenimiento"}'
```

### Eventos (4A)

```bash
curl http://localhost:8000/eventos
curl http://localhost:8000/eventos/<eid>

curl -X POST http://localhost:8000/eventos \
  -H "Content-Type: application/json" \
  -d '{"cid": "<cid-de-una-camara>", "conf_level": 0.87, "posx": 120, "posy": 340, "width": 80, "height": 200}'
```

### Analítica (4B)

```bash
# Resumen por tipo de zona
curl http://localhost:8000/analytics/zones/acceso

# Tráfico de una cámara en un rango de fechas
curl "http://localhost:8000/analytics/cameras/<cid>/traffic?from=2026-08-01&to=2026-08-31"

# Resumen de alertas de los últimos N días (default 30)
curl "http://localhost:8000/analytics/alerts/summary?days=15"
```

### Búsqueda por similitud visual (4C)

```bash
# Objetos similares a un objeto ya registrado
curl "http://localhost:8000/objects/<oid>/similar?threshold=0.25&limit=10"

# Búsqueda a partir de un embedding externo (vector de 512 floats)
curl -X POST http://localhost:8000/search/similar \
  -H "Content-Type: application/json" \
  -d '{"vector": [0.01, 0.02, "...", 0.03], "tipo": "persona", "limit": 5}'
```

El vector del ejemplo anterior debe tener exactamente 512 valores; la API rechaza con `422` cualquier vector de longitud distinta.

## Estructura del proyecto

```
.
├── endpoints.py        # Endpoints de la API (FastAPI)
├── squema.sql          # Esquema de la base de datos
├── funciones.sql       # Funciones PL/pgSQL (Fase 3)
├── triggers.sql        # Triggers de la base de datos
├── consulta.sql        # Consultas de referencia / verificación
├── seed_100.csv        # Datos de ejemplo
├── seeds.py            # Script para cargar los datos de ejemplo
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de variables de entorno
├── .env                # Configuración local (no versionado)
└── README.md
```

## Notas

- Todas las consultas se escriben en SQL puro (sin ORM), usando parámetros (`%s`) para evitar inyección SQL, tanto en los valores fijos como en las cláusulas `SET` armadas dinámicamente en los endpoints `PUT`.
- Los errores de base de datos devuelven `500` con el detalle del error de PostgreSQL, salvo el caso de violación de llave foránea al eliminar una ubicación con cámaras asociadas, que devuelve `409 Conflict`.
