-- trg_alerta_zona_peatonal: se dispara AFTER INSERT en EVENTO_DETECCION. Si el
-- evento corresponde a una cámara en zona peatonal_restringida y el objeto detectado es
-- un VEHICULO, inserta automáticamente un registro en ALERTA con severidad alta.

CREATE OR REPLACE FUNCTION verif_alerta_peatonal
RETURNS TRIGGER AS
$$
DECLARE
  e_zone VARCHAR(50);
  e_obj VARCHAR(10)

  e_cam camera%ROWTYPE;

BEGIN
  SELECT *
  INTO e_cam
  FROM camera
  WHERE CID = NEW.CID
  
  SELECT object_type
  INTO e_obj
  FROM "object"
  WHERE EID = NEW.EID

  SELECT zone_type
  INTO e_zone
  FROM "location"
  WHERE e_cam.UID = UID
  
  IF e_zone = 'zona peatonal_restringida' AND e_obj = 'vehicle' THEN
    INSERT INTO alert(
      a_AID,
      a_EID,
      a_time,
      a_severity,
      a_state,
      a_description    
    )
    VALUES(
      gen_random_uuid(),
      NEW.EID,
      NOW(),
      1,
      'pendiente',
      'El evento corresponde a una cámara en zona peatonal_restringida y el objeto detectado es un VEHICULO'
    )
  END IF;

  RETURN NEW;

END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER trg_alerta_zona_peatonal
AFTER INSERT
ON "event"
FOR EACH ROW 
EXECUTE FUNCTION verif_alerta_peatonal();



  
