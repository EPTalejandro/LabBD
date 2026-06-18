CREATE EXTENSION IF NOT EXISTS vector;
drop table if exists "location" cascade;
drop table if exists camera cascade;
drop table if exists "event" cascade;
drop table if exists alert cascade;
drop table if exists "object" cascade;
drop table if exists embedding cascade;

create table "location"(
        UID UUID DEFAULT gen_random_uuid() PRIMARY KEY ,
        "name" varchar(100) not null,
        floor varchar(3) not null,
        zone_type varchar(50) not null,
        latitude decimal(10,7) not null,
        longitude decimal(10,7) not null 
);

-- COMENTARIOS PARA LA TABLA "location"

COMMENT ON TABLE "location" IS 'Almacena la información de donde se encuentra instalada la cámara.';

COMMENT ON COLUMN "location".uid IS 'Identificador único de la ubicación.';
COMMENT ON COLUMN "location".name IS 'Nombre o descripción del lugar.';
COMMENT ON COLUMN "location".floor IS 'Nivel o piso del edificio donde se encuentra la cámara.';
COMMENT ON COLUMN "location".zone_type IS 'Tipo o clasificación de la zona.';
COMMENT ON COLUMN "location".latitude IS 'Coordenada de latitud.';
COMMENT ON COLUMN "location".longitude IS 'Coordenada de longitud.';


create table camera(
        CID UUID DEFAULT gen_random_uuid() PRIMARY key, 
        UID UUID,
        constraint fk_camera_location foreign key (UID) references "location"(UID),
        "name" varchar(20) not null,
        model varchar(100) not null,
        has_night_vision boolean not null DEFAULT false,
        "state" varchar(20) not null check ("state" in ('activa', 'en_mantenimiento', 'inactiva')) DEFAULT 'activa'     
);

-- COMENTARIOS PARA LA TABLA "camera"

COMMENT ON TABLE camera IS 'Contiene las especificaciones de la cámara.';

COMMENT ON COLUMN camera.cid IS 'Identificador único de la cámara.';
COMMENT ON COLUMN camera.uid IS 'Clave foránea que vincula la cámara con su ubicación correspondiente.';
COMMENT ON COLUMN camera.name IS 'Nombre identificativo de la cámara.';
COMMENT ON COLUMN camera.model IS 'Marca y/o modelo del hardware de la cámara.';
COMMENT ON COLUMN camera.has_night_vision IS 'Indica si el dispositivo posee capacidades de visión nocturna.';
COMMENT ON COLUMN camera.state IS 'Estado operativo actual de la cámara. Valores: activa, en_mantenimiento, inactiva.';


create table "event"(
        EID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        CID UUID,
        constraint fk_event_camera foreign key (CID) references camera(CID),
        eTime timestamptz  not null DEFAULT current_timestamp, 
        conf_level decimal(4,3) not null check (conf_level between 0 and 1),
        posX integer not null,
        posY integer not null,
        width integer not null,
        height integer not null 
);

-- COMENTARIOS PARA LA TABLA "event"

COMMENT ON TABLE "event" IS 'Registro de la detección capturada por la cámara dentro de un cuadro delimitado.';

COMMENT ON COLUMN "event".eid IS 'Identificador único del evento detectado.';
COMMENT ON COLUMN "event".cid IS 'Clave foránea que identifica la cámara que capturó el evento.';
COMMENT ON COLUMN "event".etime IS 'Fecha y hora exacta del evento, incluyendo zona horaria.';
COMMENT ON COLUMN "event".conf_level IS 'Nivel de confianza del algoritmo de detección (Rango de 0.000 a 1.000).';
COMMENT ON COLUMN "event".posx IS 'Coordenada X del punto inicial del cuadro delimitador en la imagen (píxeles).';
COMMENT ON COLUMN "event".posy IS 'Coordenada Y del punto inicial del cuadro delimitador en la imagen (píxeles).';
COMMENT ON COLUMN "event".width IS 'Ancho del cuadro delimitador del objeto detectado (píxeles).';
COMMENT ON COLUMN "event".height IS 'Alto del cuadro delimitador del objeto detectado (píxeles).';


create table alert(
        AID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        EID UUID,
        constraint fk_alert_event foreign key (EID) references "event"(EID),
        aTime timestamptz not null DEFAULT current_timestamp,
        severity varchar(10) not null check (severity in ('baja', 'media', 'alta', 'critica')),
        "state" varchar(15) not null check ("state" in ('pendiente', 'atendida', 'descartada')) DEFAULT 'pendiente',
        "description" TEXT not null 
);

-- COMENTARIOS PARA LA TABLA "alert"

COMMENT ON TABLE alert IS 'Notificación de seguridad generada a partir de un evento.';

COMMENT ON COLUMN alert.aid IS 'Identificador único de la alerta.';
COMMENT ON COLUMN alert.eid IS 'Clave foránea que conecta la alerta con el evento que la generó.';
COMMENT ON COLUMN alert.atime IS 'Fecha y hora en que se emitió la alerta, incluyendo zona horaria.';
COMMENT ON COLUMN alert.severity IS 'Nivel de gravedad del incidente. Valores: baja, media, alta, critica.';
COMMENT ON COLUMN alert.state IS 'Estado de gestión de la alerta. Valores: pendiente, atendida, descartada.';
COMMENT ON COLUMN alert.description IS 'Detalles adicionales sobre la alerta.';


create table "object"(
        OID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        EID UUID,
        constraint fk_object_event foreign key (EID) references "event"(EID),   
        object_type varchar(10) not null check (object_type in ('person', 'vehicle')),
        color varchar(50) null,
        luggage varchar(20) null check (luggage in ('mochila', 'maleta', 'maletin')),
        "vehicle" varchar(20) null check ("vehicle" in ('motocicleta', 'sedan', 'SUV', 'autobus', 'camion')),
        license_plate varchar(20) null,
        constraint chk_object_attributes
    check ((object_type = 'person'
                    and vehicle is null
                    and license_plate is null)
                or
                (object_type = 'vehicle'
                    and luggage is null))
);

-- COMENTARIOS PARA LA TABLA "object"

COMMENT ON TABLE "object" IS 'Almacena los objetos detectados asociados a un evento específico.';

COMMENT ON COLUMN "object".oid IS 'Identificador único del objeto.';
COMMENT ON COLUMN "object".eid IS 'Clave foránea que referencia al evento en el que se detectó el objeto.';
COMMENT ON COLUMN "object".object_type IS 'Tipo de objeto detectado. Valores: person, vehicle.';
COMMENT ON COLUMN "object".color IS 'Color predominante del objeto.';
COMMENT ON COLUMN "object".luggage IS 'Tipo de equipaje si el objeto es una persona. Valores: mochila, maleta, maletin.';
COMMENT ON COLUMN "object".vehicle IS 'Tipo de vehículo si el objeto es un automóvil. Valores: motocicleta, sedan, SUV, autobus, camion.';
COMMENT ON COLUMN "object".license_plate IS 'Número de matrícula visible si el objeto es un vehículo.';


create table embedding(
        EmID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        OID UUID unique not null,
        constraint fk_embedding_object foreign key (OID) references "object"(OID),
        embedding_vec vector(512) not null
);

-- COMENTARIOS PARA LA TABLA "embedding"

COMMENT ON TABLE embedding IS 'Almacena los vectores de características (embeddings) generados para el reconocimiento o búsqueda de objetos.';

COMMENT ON COLUMN embedding.emid IS 'Identificador único del registro de embedding.';
COMMENT ON COLUMN embedding.oid IS 'Clave foránea única que vincula el embedding con su objeto correspondiente (relación 1:1).';
COMMENT ON COLUMN embedding.embedding_vec IS 'Vector de 512 dimensiones que representa las características visuales del objeto.';


CREATE INDEX ON "event"(CID);
CREATE INDEX ON "event"(eTime);
CREATE INDEX ON "location"(zone_type);
CREATE INDEX ON embedding USING hnsw (embedding_vec vector_cosine_ops);
