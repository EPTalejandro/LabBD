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

create table camera(
        CID UUID DEFAULT gen_random_uuid() PRIMARY key, 
        UID UUID,
        constraint fk_camera_location foreign key (UID) references "location"(UID),
        "name" varchar(20) not null,
        model varchar(100) not null,
        has_night_vision boolean not null DEFAULT false,
        "state" varchar(20) not null check ("state" in ('activa', 'en_mantenimiento', 'inactiva')) DEFAULT 'activa'     
);

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

create table alert(
        AID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        EID UUID,
        constraint fk_alert_event foreign key (EID) references "event"(EID),
        aTime timestamptz not null DEFAULT current_timestamp,
        severity varchar(10) not null check (severity in ('baja', 'media', 'alta', 'critica')),
        "state" varchar(15) not null check ("state" in ('pendiente', 'atendida', 'descartada')) DEFAULT 'pendiente',
        "description" TEXT not null 
);

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

create table embedding(
        EmID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        OID UUID unique not null,
        constraint fk_embedding_object foreign key (OID) references "object"(OID),
        embedding_vec vector(512) not null
);


CREATE INDEX ON "event"(CID);
CREATE INDEX ON "event"(eTime);
CREATE INDEX ON "location"(zone_type);
CREATE INDEX ON embedding USING hnsw (embedding_vec vector_cosine_ops);
