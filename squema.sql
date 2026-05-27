create table ubicacion(
	UID SERIAL primary key ,
	edificio varchar(100),
	piso smallint not null,
	zonetype varchar(50) not null,
	latitud decimal(10,7) not null,
	longitud decimal(10,7) not null 
);

create table camaras(
	CID varchar(20) primary key,
	modelo varchar(100) not null,
	UID integer,
	has_night_vision boolean not null DEFAULT false,
	estado varchar(20) not null default 'activa',
	constraint UID foreign key(UID) references ubicacion
);

create table evento(
		EID SERIAL primary key,
		eTiempo timestampz default current_timestamp, 
		conf_level decimal(4,3) not null,
		posX integer not null,
		posY integer not null,
		CID varchar(20),
		constraint CID foreign key(CID) references camara,
		ancho integer not null,
		alto integer not null 
);

create table alerta(
	AID SERIAL primary key,
	EID integer,
	constraint EID foreign key(EID) references evento,
	aTiempo timestampz default current_timestamp,
	severidad varchar(10) not null,
	estado varchar(15) default 'pendiente',
	descripcion TEXT not null 
);

create table objeto(
	OID SERIAL primary key,
	EID integer,
	constraint EID foreign key(EID) references evento,
	tipo varchar(10) not null,
	color varchar(50),
	vehiculo varchar(20),
	matricula varchar(20)
);