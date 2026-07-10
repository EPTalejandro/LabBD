
create or replace function get_camera_traffic(camara_id UUID, fecha_inicio DATE, fecha_fin DATE)
returns table(total bigINT, hora numeric) AS $$
BEGIN
	return query
	select count(*) as total,extract(hour from e.eTime) as hora
	from "event" as e
	where e.CID = camara_id and e.eTime::date between fecha_inicio and fecha_fin
	group by hora
	order by hora asc;
end;
$$ language plpgsql;


select * from get_camera_traffic((select CID from camera as c where c.name= 'CAM-EST-S-01'), '2026-03-08', '2026-03-10');


create or replace function get_zone_summary(tipo_zona VARCHAR)
returns table(num_camaras bigint,num_eventos bigint,num_alertas_cri bigint) as $$
begin
	return query
	select *
	from "location" as l 
	where 
end;
$$ language plpgsql;

-- Retornar una tabla con: id del objeto encontrado, tipo, distancia coseno, nombre de la
-- cámara donde fue detectado y timestamp del evento.

create or replace function find_similar_objects(ref_id INT, threshold FLOAT, max_results INT)
returns table(object_ID UUID, object_type varchar(10), distancia_coseno vector(512), camera_name varchar(20), tiempo timestamptz)
begin
	return query
	select 
		o.OID as object_ID,
		o.object_type, 
		(em.embedding_vec <=> mv.v) as distancia_coseno
		c.name as camera_name
		e.eTime as 
	from "object" as o
	JOIN "event" as e ON o.EID = e.EID
	JOIN camera as c ON e.CID = c.CID
	
end;
