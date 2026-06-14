-- Consulta 1
SELECT 
    c.CID,
    c.nombre,
    c.modelo,
    COUNT(e.EID) AS total_detecciones
FROM camara c
JOIN evento e ON c.CID = e.CID
WHERE e.eTiempo >= NOW() - INTERVAL '30 days'
GROUP BY c.CID, c.nombre, c.modelo
ORDER BY total_detecciones DESC
LIMIT 3;


-- Consulta 2
SELECT 
    TO_CHAR(e.eTiempo AT TIME ZONE 'UTC', 'Day')    AS dia_semana,
    EXTRACT(DOW FROM e.eTiempo AT TIME ZONE 'UTC')  AS dia_num,
    o.vehiculo                                      AS tipo_vehiculo,
    COUNT(o.OID)                                    AS total
FROM objeto o
JOIN evento   e  ON o.EID  = e.EID
JOIN camara   c  ON e.CID  = c.CID
JOIN ubicacion u ON c.UID  = u.UID
WHERE u.zonetype  = 'peatonal_restringida'
  AND o.vehiculo IS NOT NULL
GROUP BY dia_semana, dia_num, o.vehiculo
ORDER BY dia_num, total DESC;


-- Consulta 3
SELECT 
    c.CID,
    c.nombre,
    c.modelo,
    ROUND(AVG(e.conf_level)::numeric, 4)    AS promedio_confianza,
    COUNT(e.EID)                            AS total_eventos
FROM camara c
JOIN evento e ON c.CID = e.CID
WHERE e.conf_level > 0.70
GROUP BY c.CID, c.nombre, c.modelo
ORDER BY promedio_confianza DESC;


-- Consulta 4
SELECT 
    c.CID,
    c.nombre,
    c.modelo,
    c.estado,
    MAX(e.eTiempo) AS ultimo_evento
FROM camara c
LEFT JOIN evento e 
       ON c.CID = e.CID 
      AND e.eTiempo >= NOW() - INTERVAL '7 days'
WHERE e.EID IS NULL
GROUP BY c.CID, c.nombre, c.modelo, c.estado
ORDER BY ultimo_evento ASC NULLS FIRST;


-- Consulta 5
SELECT 
    c.CID,
    c.nombre,
    a.severidad,
    COUNT(a.AID) AS total_alertas
FROM camara  c
JOIN evento  e ON c.CID = e.CID
JOIN alerta  a ON e.EID = a.EID
WHERE a.aTiempo >= NOW() - INTERVAL '30 days'
GROUP BY c.CID, c.nombre, a.severidad
ORDER BY c.nombre, total_alertas DESC;


-- Consulta 6
SELECT 
    o.OID,
    o.tipo,
    o.color,
    o.vehiculo,
    o.matricula,
    e.eTiempo,
    c.nombre AS camara,
    (o.embedding <=> (
        SELECT embedding 
        FROM objeto 
        WHERE embedding IS NOT NULL 
        ORDER BY OID
        LIMIT 1
    ))  AS distancia_coseno
FROM objeto o
JOIN evento e ON o.EID = e.EID
JOIN camara c ON e.CID = c.CID
WHERE o.embedding IS NOT NULL
  AND o.OID != (SELECT OID FROM objeto WHERE embedding IS NOT NULL ORDER BY OID LIMIT 1)
ORDER BY distancia_coseno ASC
LIMIT 5;


-- Consulta 7
SELECT 
    o.OID,
    o.tipo,
    o.color,
    o.equipaje,
    o.vehiculo,
    o.matricula,
    e.eTiempo,
    c.nombre AS camara,
    u.zonetype,
    (o.embedding <=> '[vector_de_referencia]'::vector) AS distancia_coseno
FROM objeto o
JOIN evento    e ON o.EID = e.EID
JOIN camara    c ON e.CID = c.CID
JOIN ubicacion u ON c.UID = u.UID
WHERE e.eTiempo >= NOW() - INTERVAL '24 hours'
  AND o.embedding IS NOT NULL
  AND (o.embedding <=> '[vector_de_referencia]'::vector) < 0.15
ORDER BY distancia_coseno ASC;