# -*- coding: utf-8 -*-
"""
Módulo de Consultas Cruzadas y Validaciones Especiales (Others_Querys)
---------------------------------------------------------------------
Este módulo contiene consultas SQL avanzadas (cláusulas WHERE) diseñadas para realizar
validaciones de integridad referencial, consistencia espacial y cruces de datos entre 
diferentes capas geográficas y tablas tabulares del sistema SIGELEC.
"""

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "PUNTO DE CARGA" (Acometidas de Clientes)
# ==============================================================================

# Valida que la cantidad de clientes (relaciones físicas) en la tabla ConexionConsumidor 
# coincida con la cantidad de códigos de clientes concatenados (separados por ';') 
# en el campo CODIGOCLIENTE del Punto de Carga.
query_PC01 = '''
GLOBALID IN (SELECT CC.PUNTOCARGAGLOBALID
FROM SIGELEC.CONEXIONCONSUMIDOR CC 
GROUP BY CC.PUNTOCARGAGLOBALID 
HAVING COUNT(*)<>(SELECT REGEXP_COUNT(CODIGOCLIENTE, ';') 
FROM SIGELEC.PUNTOCARGA 
WHERE GLOBALID=CC.PUNTOCARGAGLOBALID)+1)
'''

# Valida que la cantidad de medidores registrados en la tabla ConexionConsumidor 
# coincida con la cantidad de números de medidores concatenados (separados por ';') 
# en el campo MEDIDOR del Punto de Carga.
query_PC02 = '''
GLOBALID IN (SELECT CC.PUNTOCARGAGLOBALID
FROM SIGELEC.CONEXIONCONSUMIDOR CC 
GROUP BY CC.PUNTOCARGAGLOBALID 
HAVING COUNT(*)<>(SELECT REGEXP_COUNT(MEDIDOR, ';') 
FROM SIGELEC.PUNTOCARGA 
WHERE GLOBALID=CC.PUNTOCARGAGLOBALID)+1)
'''

# Valida que la cantidad de secuencias de lectura en la tabla ConexionConsumidor 
# coincida con la cantidad de secuencias concatenadas (separadas por ';') 
# en el campo SECUENCIALECTURA del Punto de Carga.
query_PC03 = '''
GLOBALID IN (SELECT CC.PUNTOCARGAGLOBALID
FROM SIGELEC.CONEXIONCONSUMIDOR CC 
GROUP BY CC.PUNTOCARGAGLOBALID 
HAVING COUNT(*)<>(SELECT REGEXP_COUNT(SECUENCIALECTURA, ';') 
FROM SIGELEC.PUNTOCARGA 
WHERE GLOBALID=CC.PUNTOCARGAGLOBALID)+1)
'''

# Valida la consistencia de conectividad del Punto de Carga: identifica si el 
# transformador de distribución relacionado (PARENTCIRCUITSOURCEGUID) pertenece a un 
# alimentador (ALIMENTADORID) diferente al que tiene asignado el propio Punto de Carga.
query_PC04 = '''
PARENTCIRCUITSOURCEGUID IN (SELECT T.CIRCUITSOURCEGUID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T 
WHERE T.CIRCUITSOURCEGUID = SIGELEC.PuntoCarga.PARENTCIRCUITSOURCEGUID 
AND T.ALIMENTADORID <> SIGELEC.PuntoCarga.ALIMENTADORID)
'''

# Puntos de carga que contienen clientes con códigos de ruta comercial (CLIRLSCOD) diferentes 
# (inconsistencia comercial de agrupación), excluyendo a clientes en estados inactivos o de baja (E, I, F).
query_PC05 = '''
GLOBALID IN ( 
SELECT CC.PUNTOCARGAGLOBALID 
FROM SIGELEC.CONEXIONCONSUMIDOR CC 
INNER JOIN SIGELEC.ATRIBUTOSCONSUMIDOR AC 
ON (CC.CODIGOUNICO = AC.CODIGOUNICO 
AND SUBSTR(AC.CLIRLSCOD,5,1) NOT IN ('E','I', 'F'))
GROUP BY  CC.PUNTOCARGAGLOBALID 
HAVING COUNT (DISTINCT AC.CLIRLSCOD)>1)
'''

# Identifica medidores comerciales clasificados como "GRANDES CLIENTES" (en atributos)
# que se encuentran conectados a transformadores de distribución de propiedad pública 
# (deberían estar conectados a transformadores particulares / privados).
query_PC06 = '''
GLOBALID IN (
SELECT CC.PUNTOCARGAGLOBALID 
FROM SIGELEC.CONEXIONCONSUMIDOR CC
INNER JOIN SIGELEC.ATRIBUTOSCONSUMIDOR AC
ON CC.CODIGOUNICO = AC.CODIGOUNICO
WHERE AC.AGENCIA = 'GRANDES CLIENT') 
AND PARENTCIRCUITSOURCEGUID IN (
SELECT T.CIRCUITSOURCEGUID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T
WHERE T.PROPIEDAD <> 'PARTICULAR')
'''

# Puntos de carga que contienen clientes con códigos de cantón/parroquia comercial 
# (CLIPARCOD) diferentes dentro del mismo punto de entrega física.
query_PC07 = '''
GLOBALID IN ( 
SELECT CC.PUNTOCARGAGLOBALID 
FROM SIGELEC.CONEXIONCONSUMIDOR CC 
INNER JOIN SIGELEC.ATRIBUTOSCONSUMIDOR AC 
ON CC.CODIGOUNICO = AC.CODIGOUNICO
GROUP BY  CC.PUNTOCARGAGLOBALID 
HAVING COUNT (DISTINCT AC.CLIPARCOD)>1)
'''

# Valida que los puntos de carga de subtipo 6 (medidores concentradores) tengan 
# más de una conexión de consumidor registrada (un concentrador por definición 
# debe agrupar a múltiples clientes/medidores individuales).
query_PC08 = '''
SUBTIPO = 6 AND GLOBALID IN (
SELECT CC.PUNTOCARGAGLOBALID
FROM SIGELEC.CONEXIONCONSUMIDOR CC
GROUP BY CC.PUNTOCARGAGLOBALID
HAVING COUNT (*)>1)
'''

# Selecciona los puntos de carga que no están vinculados a ningún tramo de baja tensión 
# (aéreo o subterráneo) a través de su TRAMOGLOBALID, exceptuando subtipos 6 y 9 (casos especiales).
query_PC09 = '''
GLOBALID NOT IN (SELECT PC.GLOBALID 
FROM SIGELEC.PUNTOCARGA PC
INNER JOIN SIGELEC.TRAMOBAJATENSIONAEREO T
ON PC.TRAMOGLOBALID = T.GLOBALID ) AND 
GLOBALID NOT IN (SELECT PC.GLOBALID 
FROM SIGELEC.PUNTOCARGA PC
INNER JOIN SIGELEC.TRAMOBAJATENSIONSUBTERRANEO S
ON PC.TRAMOGLOBALID = S.GLOBALID ) AND SUBTIPO NOT IN ( 6 , 9 )
'''

# Identifica puntos de carga vinculados a tramos de BT cuyo subtipo no corresponde a 
# acometidas (los subtipos de acometidas válidos en tramo BT son 7, 8 o 9), exceptuando 
# puntos de carga de subtipo 6 y 9.
query_PC10 = '''
GLOBALID IN (SELECT PC.GLOBALID 
FROM SIGELEC.PUNTOCARGA PC
INNER JOIN SIGELEC.TRAMOBAJATENSIONAEREO T
ON PC.TRAMOGLOBALID = T.GLOBALID
WHERE  T.SUBTIPO NOT IN (7, 8, 9)) 
AND SUBTIPO NOT IN ( 6 , 9 )
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA TABLA "CONEXIONCONSUMIDOR"
# ==============================================================================

# Valida que el secuencial de inmueble (CLISECINM) de la tabla comercial de atributos 
# de consumidor coincida con el registrado en ConexionConsumidor para el mismo código único,
# omitiendo registros con novedades 4 y 5 o secuenciales nulos.
query_CC01 = '''
(CODIGOUNICO IN (SELECT AC.CODIGOUNICO
FROM SIGELEC.ATRIBUTOSCONSUMIDOR AC
WHERE SIGELEC.CONEXIONCONSUMIDOR.CLISECINM<>AC.CLISECINM) 
OR CLISECINM IS NULL) AND NOVEDADES NOT IN('4','5')
'''

# Valida que el número de fabricación del medidor (MDENUMFAB) de la conexión coincida 
# con el número de medidor comercial (NUMMEDIDOR) en atributos del consumidor,
# exceptuando novedades 4, 5 y medidores vacíos.
query_CC02 = '''
(CODIGOCLIENTE IN (SELECT AC.CODIGOCLIENTE
FROM SIGELEC.ATRIBUTOSCONSUMIDOR AC
WHERE SIGELEC.CONEXIONCONSUMIDOR.MDENUMFAB<>AC.NUMMEDIDOR 
AND AC.NUMMEDIDOR NOT IN (' ')) OR MDENUMFAB IS NULL) 
AND NOVEDADES NOT IN('4','5')
'''

# Valida que la correspondencia comercial sea correcta detectando si el código de cliente 
# (CODIGOCLIENTE) registrado en la conexión no coincide con el de la tabla de atributos,
# omitiendo novedades 4 y 5 o códigos nulos.
query_CC03 = '''(MEDIDOR IN (SELECT AC.MEDIDOR
FROM SIGELEC.ATRIBUTOSCONSUMIDOR AC
WHERE SIGELEC.CONEXIONCONSUMIDOR.CODIGOCLIENTE<>AC.CODIGOCLIENTE) 
OR CODIGOCLIENTE IS NULL) AND NOVEDADES NOT IN('4','5')
'''

# Valida consistencia geográfica administrativa: verifica si la provincia, cantón 
# o parroquia registrados en ConexionConsumidor difieren de los de su Punto de Carga asociado.
query_CC04 = '''
PUNTOCARGAGLOBALID IN(SELECT PC.GLOBALID 
FROM SIGELEC.PUNTOCARGA PC WHERE PC.GLOBALID = PUNTOCARGAGLOBALID 
AND (SIGELEC.CONEXIONCONSUMIDOR.PROVINCIA <> PC.PROVINCIA 
OR SIGELEC.CONEXIONCONSUMIDOR.CANTON <> PC.CANTON OR 
SIGELEC.CONEXIONCONSUMIDOR.PARROQUIA <> PC.PARROQUIA))
'''

# Selecciona las conexiones de consumidor cuyas acometidas están asociadas a voltajes de 
# distribución bifásicos o trifásicos (208, 220 o 240V) pero cuya secuencia de fase o 
# circuito corresponde incorrectamente a niveles monofásicos a 120 o 127V (e.g. fase simple 'a', 'b', 'c').
query_CC05 = '''
PUNTOCARGAGLOBALID IN (SELECT PC.GLOBALID FROM SIGELEC.PUNTOCARGA PC 
WHERE PC.TRAMOGLOBALID IN (SELECT T.GLOBALID FROM SIGELEC.TramoBajaTensionAereo T 
WHERE T.VOLTAJE IN (208,220,240)) AND (SECUENCIAFASE IN ( 'a', 'b', 'c') 
OR CIRCUITOS IN('A', 'B', 'C', 'F1', 'F2'))) AND MIESTADO='CAMBIO' 
'''

# Selecciona las conexiones de consumidor cuyas acometidas están asociadas a voltajes de 
# distribución monofásicos (120 o 127V) pero cuya secuencia de fase o circuito corresponde 
# incorrectamente a niveles bifásicos o trifásicos a 220 o 240V (e.g. 'ab', 'abc', 'ac', 'bc').
query_CC06 = '''
PUNTOCARGAGLOBALID IN (SELECT PC.GLOBALID FROM SIGELEC.PUNTOCARGA PC 
WHERE PC.TRAMOGLOBALID IN (SELECT T.GLOBALID FROM SIGELEC.TramoBajaTensionAereo T 
WHERE T.VOLTAJE IN (120,127)) AND (SECUENCIAFASE IN ( 'ab', 'abc', 'ac', 'bc') 
OR CIRCUITOS IN('AB', 'ABC', 'AC', 'BC', 'F12')))
'''

# Identifica registros en ConexionConsumidor que tienen asignado un CODIGOUNICO de cliente 
# que no existe en la tabla de atributos comerciales (ATRIBUTOSCONSUMIDOR) (inconsistencia de integridad).
query_CC07 = '''
CODIGOUNICO NOT IN ( SELECT AC.CODIGOUNICO
FROM SIGELEC.ATRIBUTOSCONSUMIDOR AC
WHERE AC.CODIGOUNICO = SIGELEC.CONEXIONCONSUMIDOR.CODIGOUNICO 
AND SIGELEC.CONEXIONCONSUMIDOR.CODIGOUNICO IS NOT NULL)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "PUESTO TRANSFORMADOR DISTRIBUCION"
# ==============================================================================

# Valida consistencia geográfica: verifica si la provincia, cantón o parroquia del 
# puesto físico del transformador difiere de los registrados en su Unidad física asociada.
query_PTD01 = '''
GLOBALID IN(SELECT UT.PUESTOTRANSFDISTGLOBALID 
FROM SIGELEC.UNIDADTRANSFDISTRIBUCION UT 
WHERE GLOBALID = UT.PUESTOTRANSFDISTGLOBALID 
AND (SIGELEC.PUESTOTRANSFDISTRIBUCION.PROVINCIA <> UT.PROVINCIA
OR SIGELEC.PUESTOTRANSFDISTRIBUCION.CANTON <> UT.CANTON 
OR SIGELEC.PUESTOTRANSFDISTRIBUCION.PARROQUIA <> UT.PARROQUIA))
'''

# Valida integridad del código del transformador: el código TRAFO del puesto geográfico 
# debe coincidir con el CODIGOUNIDAD de la unidad de transformador física relacionada,
# exceptuando subestaciones o bancos especiales de subtipos 9, 10, 11 y 12.
query_PTD02 = '''
GLOBALID IN(SELECT UT.PUESTOTRANSFDISTGLOBALID 
FROM SIGELEC.UNIDADTRANSFDISTRIBUCION UT 
WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.GLOBALID = UT.PUESTOTRANSFDISTGLOBALID 
AND SIGELEC.PUESTOTRANSFDISTRIBUCION.TRAFO <> UT.CODIGOUNIDAD) 
AND SUBTIPO NOT IN ( 9, 10, 11, 12)
'''

# Valida consistencia de voltaje: comprueba que el voltaje del transformador sea coherente 
# con la tensión nominal del alimentador del circuito fuente al que está conectado 
# (e.g. alimentador de 13.8kV debe albergar transformadores de 13.8kV, 7.9kV, 7.6kV; y alimentador de 34.5kV los de 34.5kV o 19.9kV).
query_PTD03 = '''
GLOBALID IN (SELECT T.GLOBALID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T
INNER JOIN SIGELEC.CIRCUITOFUENTE CF
ON T.ALIMENTADORID = CF.CODIGOALIMENTADOR
WHERE (CF.TENSIONNOMINAL = 13800 AND T.VOLTAJE NOT IN ( 13800, 7967, 7621)) 
OR (CF.TENSIONNOMINAL = 34500 AND T.VOLTAJE NOT IN ( 34500, 19919)))
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA TABLA "UNIDADTRANSFDISTRIBUCION"
# ==============================================================================

# Valida consistencia geográfica: verifica si la provincia, cantón o parroquia de la 
# unidad de transformador difiere de los del puesto geográfico relacionado (PTD).
query_UT01 = '''
PUESTOTRANSFDISTGLOBALID IN(SELECT PTD.GLOBALID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION PTD 
WHERE PTD.GLOBALID = PUESTOTRANSFDISTGLOBALID 
AND (SIGELEC.UNIDADTRANSFDISTRIBUCION.PROVINCIA <> PTD.PROVINCIA 
OR SIGELEC.UNIDADTRANSFDISTRIBUCION.CANTON <> PTD.CANTON 
OR SIGELEC.UNIDADTRANSFDISTRIBUCION.PARROQUIA <> PTD.PARROQUIA))
'''

# Segunda validación de consistencia geográfica entre la unidad de transformador (UT) y el puesto (PTD).
query_UT02 = '''
PUESTOTRANSFDISTGLOBALID IN (SELECT T.GLOBALID FROM 
SIGELEC.Puestotransfdistribucion T WHERE 
T.PROVINCIA<>SIGELEC.UNIDADTRANSFDISTRIBUCION.PROVINCIA OR 
T.CANTON<>SIGELEC.UNIDADTRANSFDISTRIBUCION.CANTON OR 
T.PARROQUIA<>SIGELEC.UNIDADTRANSFDISTRIBUCION.PARROQUIA)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "PUESTOSECCIONADORFUSIBLE" (Cutouts)
# ==============================================================================

# Valida consistencia geográfica: verifica si la provincia, cantón o parroquia del 
# puesto del seccionador fusible difiere de la de su unidad física relacionada (UnidadFusible).
query_PSF01 = '''
GLOBALID IN(SELECT UF.PUESTOSECFUSIBLEGLOBALID 
FROM SIGELEC.UNIDADFUSIBLE UF WHERE GLOBALID = UF.PUESTOSECFUSIBLEGLOBALID 
AND (SIGELEC.PUESTOSECCIONADORFUSIBLE.PROVINCIA <> UF.PROVINCIA
OR SIGELEC.PUESTOSECCIONADORFUSIBLE.CANTON <> UF.CANTON 
OR SIGELEC.PUESTOSECCIONADORFUSIBLE.PARROQUIA <> UF.PARROQUIA))
'''

# Valida consistencia de voltaje: comprueba que el voltaje del seccionador fusible sea coherente 
# con la tensión nominal del alimentador del circuito fuente al que está conectado.
query_PSF02 = '''
GLOBALID IN (SELECT S.GLOBALID 
FROM SIGELEC.PUESTOSECCIONADORFUSIBLE S
INNER JOIN SIGELEC.CIRCUITOFUENTE CF
ON S.ALIMENTADORID = CF.CODIGOALIMENTADOR
WHERE (CF.TENSIONNOMINAL = 13800 AND S.VOLTAJE NOT IN ( 13800, 7967, 7621)) 
OR (CF.TENSIONNOMINAL = 34500 AND S.VOLTAJE NOT IN ( 34500, 19919)))
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA TABLA "UNIDADFUSIBLE"
# ==============================================================================

# Valida consistencia geográfica: comprueba si la provincia, cantón o parroquia de la 
# unidad de fusible difiere de la del puesto geográfico relacionado (PSF).
query_UF01 = '''
PUESTOSECFUSIBLEGLOBALID IN(SELECT PSF.GLOBALID 
FROM SIGELEC.PUESTOSECCIONADORFUSIBLE PSF 
WHERE PSF.GLOBALID = PUESTOSECFUSIBLEGLOBALID 
AND (SIGELEC.UNIDADFUSIBLE.PROVINCIA <> PSF.PROVINCIA
OR SIGELEC.UNIDADFUSIBLE.CANTON <> PSF.CANTON 
OR SIGELEC.UNIDADFUSIBLE.PARROQUIA <> PSF.PARROQUIA))
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "ESTRUCTURASOPORTE" (Postes)
# ==============================================================================

# Valida la correspondencia física de estructuras: la cantidad de códigos de estructuras 
# concatenados (separados por ';') en el campo ESTRUCTURAENPOSTE del poste debe coincidir 
# con la cantidad de registros relacionados en la tabla intermedia EstructuraEnPoste.
query_ES01 = '''
GLOBALID IN (SELECT ES.ESTRUCTURASOPORTEGLOBALID
FROM SIGELEC.ESTRUCTURAENPOSTE ES
GROUP BY ES.ESTRUCTURASOPORTEGLOBALID
HAVING COUNT(*)<>(SELECT REGEXP_COUNT(ESTRUCTURAENPOSTE, ';')
FROM SIGELEC.ESTRUCTURASOPORTE 
WHERE GLOBALID=ES.ESTRUCTURASOPORTEGLOBALID)+1)
'''

# Valida consistencia geográfica: comprueba que el poste geográfico y sus estructuras asociadas 
# en la tabla EstructuraEnPoste tengan los mismos códigos de provincia, cantón y parroquia.
query_ES02 = '''
GLOBALID IN(SELECT ESP.ESTRUCTURASOPORTEGLOBALID 
FROM SIGELEC.ESTRUCTURAENPOSTE ESP WHERE GLOBALID = ESP.ESTRUCTURASOPORTEGLOBALID 
AND (SIGELEC.ESTRUCTURASOPORTE.PROVINCIA <> ESP.PROVINCIA
OR SIGELEC.ESTRUCTURASOPORTE.CANTON <> ESP.CANTON 
OR SIGELEC.ESTRUCTURASOPORTE.PARROQUIA <> ESP.PARROQUIA))
'''

# Identifica postes de soporte que tienen asignada de forma duplicada la estructura 'EST0019' 
# (inconsistencia física en el armado del poste).
query_ES03 = ''' 
GLOBALID IN (SELECT ES.ESTRUCTURASOPORTEGLOBALID 
FROM SIGELEC.ESTRUCTURAENPOSTE ES 
WHERE REGEXP_LIKE ( ES.CODIGOESTRUCTURA, 'EST0019') 
GROUP BY ES.ESTRUCTURASOPORTEGLOBALID 
HAVING COUNT(*) >1 )
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA TABLA "ESTRUCTURAENPOSTE"
# ==============================================================================

# Valida consistencia geográfica: comprueba si la provincia, cantón o parroquia de la 
# estructura en poste difiere de la del poste geográfico relacionado de soporte.
query_ESP01 = '''
ESTRUCTURASOPORTEGLOBALID IN(SELECT P.GLOBALID 
FROM SIGELEC.ESTRUCTURASOPORTE P WHERE P.GLOBALID = ESTRUCTURASOPORTEGLOBALID 
AND (SIGELEC.ESTRUCTURAENPOSTE.PROVINCIA <> P.PROVINCIA
OR SIGELEC.ESTRUCTURAENPOSTE.CANTON <> P.CANTON 
OR SIGELEC.ESTRUCTURAENPOSTE.PARROQUIA <> P.PARROQUIA))
'''

# Segunda validación de consistencia geográfica entre la estructura en poste y el poste geográfico de soporte (Poste).
query_ESP02 = '''
ESTRUCTURASOPORTEGLOBALID IN (SELECT P.GLOBALID FROM 
SIGELEC.ESTRUCTURASOPORTE P 
WHERE P.PROVINCIA<>SIGELEC.ESTRUCTURAENPOSTE.PROVINCIA OR 
P.CANTON<>SIGELEC.ESTRUCTURAENPOSTE.CANTON OR 
P.PARROQUIA<>SIGELEC.ESTRUCTURAENPOSTE.PARROQUIA)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "TRAMO BAJA TENSION AEREO" (Acometidas Aéreas)
# ==============================================================================

# Identifica tramos de BT aéreos monofásicos (voltaje 120 o 127V) asociados a puntos de carga 
# con estado de modificación específico 'CAMBIO' y proyecto 'SERVI-025-DC-2023' 
# (se espera que estas acometidas sean modificadas a otros voltajes).
query_BTA01 = '''
GLOBALID IN (SELECT PC.TRAMOGLOBALID FROM SIGELEC.PUNTOCARGA PC 
WHERE PC.GLOBALID IN (SELECT CC.PUNTOCARGAGLOBALID FROM SIGELEC.CONEXIONCONSUMIDOR CC 
WHERE CC.MIESTADO='CAMBIO' AND PROYECTOMODIFICACION = 'SERVI-025-DC-2023')) 
AND VOLTAJE IN ( 120, 127)
'''

# Valida consistencia de conectividad: identifica si el tramo de BT aéreo está asociado a un 
# transformador padre (PARENTCIRCUITSOURCEGUID) cuyo alimentador (ALIMENTADORID) difiere 
# del asignado al propio tramo de BT.
query_BTA02 = '''
PARENTCIRCUITSOURCEGUID IN (SELECT T.CIRCUITSOURCEGUID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T 
WHERE T.CIRCUITSOURCEGUID = SIGELEC.TRAMOBAJATENSIONAEREO.PARENTCIRCUITSOURCEGUID 
AND T.ALIMENTADORID <> SIGELEC.TRAMOBAJATENSIONAEREO.ALIMENTADORID)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "LUMINARIA"
# ==============================================================================

# Valida consistencia de conectividad: identifica si el puesto de luminaria está asociado a un 
# transformador padre (PARENTCIRCUITSOURCEGUID) cuyo alimentador (ALIMENTADORID) difiere 
# del asignado a la luminaria.
query_LUM01 = '''
PARENTCIRCUITSOURCEGUID IN (SELECT T.CIRCUITSOURCEGUID 
FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T 
WHERE T.CIRCUITSOURCEGUID = SIGELEC.Luminaria.PARENTCIRCUITSOURCEGUID 
AND T.ALIMENTADORID <> SIGELEC.luminaria.ALIMENTADORID)
'''

# Inconsistencia espacial: selecciona las luminarias que están situadas geográficamente 
# a una distancia lineal mayor a 2 metros de la coordenada física del poste relacionado (P) 
# en base de datos (calculado mediante Pitágoras sobre coordenadas geométricas).
query_LUM02 = '''
GLOBALID IN( 
SELECT L.GLOBALID 
FROM SIGELEC.LUMINARIA L
INNER JOIN SIGELEC.ESTRUCTURASOPORTE P 
ON P.GLOBALID = L.ESTRUCTURASOPORTEGLOBALID 
WHERE SQRT(POWER((SDE.ST_X(L.SHAPE) - P.COORD_X),2) + 
POWER((SDE.ST_Y(L.SHAPE) - P.COORD_Y),2))>2)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "POSTE" (Estructuras de Soporte)
# ==============================================================================

# Identifica postes de uso general (excluyendo postes de uso especial 1, 5, 6, 7, 8, 9, 10) 
# que no tienen ninguna estructura física asignada en la tabla relacionada EstructuraEnPoste.
query_POS01 = '''
TIPOUSOPOSTE  not in ( 1 , 5 , 6 , 7, 8 , 9 , 10) 
AND GLOBALID IN (SELECT P.GLOBALID FROM SIGELEC.ESTRUCTURASOPORTE P 
WHERE NOT EXISTS ( SELECT 1 FROM SIGELEC.ESTRUCTURAENPOSTE ES 
WHERE P.GLOBALID = ES.ESTRUCTURASOPORTEGLOBALID))
'''

# Valida consistencia en el recuento de estructuras del poste: comprueba que el recuento de registros 
# en la tabla EstructuraEnPoste coincida con el número de códigos de estructura concatenados en el poste.
query_POS02 = '''
GLOBALID IN (SELECT ES.ESTRUCTURASOPORTEGLOBALID
FROM SIGELEC.ESTRUCTURAENPOSTE ES
GROUP BY ES.ESTRUCTURASOPORTEGLOBALID 
HAVING COUNT(*)<>(SELECT REGEXP_COUNT(SIGELEC.ESTRUCTURASOPORTE.ESTRUCTURAENPOSTE, ';') 
FROM SIGELEC.ESTRUCTURASOPORTE 
WHERE GLOBALID=ES.ESTRUCTURASOPORTEGLOBALID)+1)
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "TRAMOS DISTRIBUCION AEREO" (Media Tensión)
# ==============================================================================

# Valida consistencia de voltaje: comprueba que el voltaje del tramo de media tensión sea coherente 
# con la tensión nominal del alimentador del circuito fuente asignado.
query_MTA03 = '''
GLOBALID IN (SELECT T.GLOBALID 
FROM SIGELEC.tramodistribucionaereo T
INNER JOIN SIGELEC.CIRCUITOFUENTE CF
ON T.ALIMENTADORID = CF.CODIGOALIMENTADOR
WHERE (CF.TENSIONNOMINAL = 13800 AND T.VOLTAJE NOT IN ( 13800, 7967, 7621)) 
OR (CF.TENSIONNOMINAL = 34500 AND T.VOLTAJE NOT IN ( 34500, 19919)))
'''

# ==============================================================================
# CONSULTAS DE VALIDACIÓN PARA LA CAPA "TENSOR"
# ==============================================================================

# Inconsistencia de ubicación del tensor: selecciona los tensores cuyas coordenadas geométricas 
# (redondeadas a 0 decimales) difieren de las del poste de soporte físico al cual están relacionados.
query_TE01 = '''
GLOBALID IN( 
SELECT T.GLOBALID 
FROM SIGELEC.TENSOR T 
INNER JOIN SIGELEC.ESTRUCTURASOPORTE P 
ON P.GLOBALID = T.ESTRUCTURASOPORTEGLOBALID 
WHERE ROUND(SDE.ST_X(T.SHAPE),0)<>ROUND(P.COORD_X,0) 
OR ROUND(SDE.ST_Y(T.SHAPE),0)<>ROUND(P.COORD_Y,0))
'''