-- trg_alerta_zona_peatonal: se dispara AFTER INSERT en EVENTO_DETECCION. Si el
-- evento corresponde a una cámara en zona peatonal_restringida y el objeto detectado es
-- un VEHICULO, inserta automáticamente un registro en ALERTA con severidad alta.

CREATE OR REPLACE FUNCTION verif_alerta_peatonal()
RETURNS TRIGGER AS
$$
DECLARE
  e_zone VARCHAR(50);

  e_cam camera%ROWTYPE;
  e_ev "event"%ROWTYPE;

BEGIN
  SELECT *
  INTO e_ev 
  FROM "event"
  WHERE EID = NEW.EID;

  SELECT *
  INTO e_cam
  FROM camera
  WHERE CID = e_ev.CID;
  
  SELECT zone_type
  INTO e_zone
  FROM "location"
  WHERE e_cam.UID = UID;
  
  IF e_zone = 'peatonal_restringida' AND NEW.object_type = 'vehicle' THEN
    INSERT INTO alert(
      AID,
      EID,
      aTime,
      severity,
      "state",
      description    
    )
    VALUES(
      gen_random_uuid(),
      NEW.EID,
      NOW(),
      'alta',
      'pendiente',
      'El evento corresponde a una cámara en zona peatonal_restringida y el objeto detectado es un VEHICULO'
    );
  END IF;

  RETURN NEW;

END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER trg_alerta_zona_peatonal
AFTER INSERT
ON "object"
FOR EACH ROW 
EXECUTE FUNCTION verif_alerta_peatonal();

-- trg_audit_camara: se dispara AFTER UPDATE en CAMARA. Si el campo estado cambia a
-- inactiva, inserta un registro en una tabla AUDITORIA_CAMARA (que el equipo debe
-- diseñar e incluir en el DDL) con el id de la cámara, la fecha del cambio y el estado anterior.





  
