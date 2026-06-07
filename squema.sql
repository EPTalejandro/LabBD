CREATE EXTENSION IF NOT EXISTS vector;
drop table if exists ubicacion cascade;
drop table if exists camara cascade;
drop table if exists evento cascade;
drop table if exists alerta cascade;
drop table if exists objeto cascade ;

create table ubicacion(
	UID UUID DEFAULT gen_random_uuid() PRIMARY KEY ,
	edificio varchar(100),
	piso smallint not null,
	zonetype varchar(50) not null,
	latitud decimal(10,7) not null,
	longitud decimal(10,7) not null 
);

create table camara(
	CID varchar(20) PRIMARY KEY,
	modelo varchar(100) not null,
	UID UUID,
	has_night_vision boolean not null DEFAULT false,
	estado varchar(20) not null default 'activa',
	constraint UID foreign key(UID) references ubicacion
);

create table evento(
		EID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
		eTiempo timestamptz default current_timestamp, 
		conf_level decimal(4,3) not null,
		posX integer not null,
		posY integer not null,
		CID varchar(20),
		constraint CID foreign key(CID) references camara,
		ancho integer not null,
		alto integer not null 
);

create table alerta(
	AID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
	EID UUID,
	constraint EID foreign key(EID) references evento,
	aTiempo timestamptz default current_timestamp,
	severidad varchar(10) not null,
	estado varchar(15) default 'pendiente',
	descripcion TEXT not null 
);

create table objeto(
	OID UUID DEFAULT gen_random_uuid() PRIMARY KEY,
	EID UUID,
	constraint EID foreign key(EID) references evento,
	tipo varchar(10) not null,
	color varchar(50),
	vehiculo varchar(20),
	matricula varchar(20),
	embedding vector(512)
);

