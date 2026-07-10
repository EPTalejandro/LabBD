
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

--DROP FUNCTION get_zone_summary(character varying)

create or replace function get_zone_summary(tipo_zona VARCHAR)
returns table(nombre varchar,num_camaras bigint,num_eventos bigint,num_alertas_criticas bigint) as $$
begin
	return query
	select l.name,count(distinct c.CID) filter(where c.state= 'activa'),count(e.EID),count(a.AID) filter (where a.severity= 'critica')
	from "location" as l 
	join "camera" as c on c.UID = l.UID
	left join "event" as e on e.CID = c.CID
	left join alert as a on a.EID = e.EID
	where l.zone_type = tipo_zona
	group by l.UID;
end;
$$ language plpgsql;

select * from get_zone_summary('estacionamiento');

