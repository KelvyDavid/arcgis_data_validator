# ==============================================================================
# Enterprise_Querys.py
# ==============================================================================
# Módulo de queries de validación específicas de la empresa. Contiene consultas SQL (cláusulas WHERE) para detectar errores
# en los datos GIS de la red de distribución eléctrica.
#
# Las validaciones incluyen:
#   - Barras, Tramos MT, Tramos BT y Subtransmisión
#   - Protección Dinámica, Regulador de Tensión, Seccionadores
#   - Transformadores de Distribución y de Potencia
#   - Puntos de Carga, Luminarias, Semáforos
#   - Postes, Tensores, Estructuras Subterráneas
#   - Circuito Fuente, Unidades de equipos
#   - Equipos y Tramos de Telecomunicaciones
#   - Validaciones de SISTOT (órdenes de trabajo)
#
# Cada constante almacena una cláusula WHERE que, al ejecutarse con arcpy,
# selecciona los registros con error (que NO cumplen la regla de negocio).
# ==============================================================================

# ==========================================
# Queries comunes reutilizables
# ==========================================

# Valida que el código de empresa sea 'COD_EMPRESA' (no nulo ni diferente)
Enterprise_CodigoEmpresa = '''CODIGOEMPRESA IS NULL OR CODIGOEMPRESA NOT IN ('COD_EMPRESA')'''

# Valida que los campos de ubicación geográfica no sean nulos ni vacíos
Enterprise_ProvCantParr = '''(PROVINCIA is null or CANTON is null or PARROQUIA is null or 
                        PROVINCIA =  '' or CANTON = '' or PARROQUIA = '')'''

# Valida la consistencia jerárquica de los códigos geográficos:
# - Los 2 primeros dígitos de CANTON deben coincidir con PROVINCIA
# - Los 4 primeros dígitos de PARROQUIA deben coincidir con CANTON
Enterprise_ConsistenciaProvCantParr = "((PROVINCIA <> substr(CANTON, 0,2)) or (CANTON <> substr(PARROQUIA, 0,4)))"

# Valida que el campo ORDENTRABAJO no contenga letras (debe ser numérico)
# Se usa para detectar órdenes de trabajo de SISTOT con formato incorrecto
Enterprise_ot_Sistot = "ORDENTRABAJO is not null and REGEXP_LIKE(ORDENTRABAJO,'[a-zA-Z]+')"

# ==============================================================================
# QUERIES PARA CAPA "BARRAS"
# ==============================================================================

# Valida código de empresa en barras
Enterprise_BAR01 = Enterprise_CodigoEmpresa

# ==============================================================================
# QUERIES PARA CAPA "TRAMOS MT" (Media Tensión)
# ==============================================================================

# Bajantes (subtipo >= 4) con longitud incorrecta: mayor a 3m o menor a 20cm
Enterprise_MT07 = "(SHAPE.LEN >3 OR SHAPE.LEN < 0.2) and subtipo >= 4"

# Tramos MT con alimentador asignado pero que NO admiten traces (trazado de red)
Enterprise_MT08 = "ALIMENTADORID IS NOT NULL AND (FDRMGRNONTRACEABLE IN (1))"

# Tramos MT con alimentador asignado pero con estado ENABLED = 0 (deshabilitado)
Enterprise_MT09 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Tramos MT sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_MT10 = Enterprise_ConsistenciaProvCantParr

# Tramos MT sin Provincia, Cantón o Parroquia
Enterprise_MT11 = Enterprise_ProvCantParr


# ==============================================================================
# QUERIES PARA CAPA "PUESTO PROTECCIÓN DINÁMICO"
# ==============================================================================

# Protección dinámica sin tipo de control o con valor no válido
# (debe ser 'Manual' o 'Telecomandado')
Enterprise_PPD09 = "control IS NULL OR control NOT IN ( 'Manual' , 'Telecomandado')"

# Protección dinámica con SUBSOURCE = 1 (cabecera) pero sin relación a CircuitoFuente,
# o con subsource nulo
Enterprise_PPD10 = '''((subsource is null or globalid NOT IN (select c.PUESTOPROTDINAMGLOBALID FROM sigelec.circuitofuente c 
                WHERE c.globalid IS NOT NULL))) AND subsource = 1'''

# Protección dinámica con TIPOUSO nulo o no válido
# (debe ser 'Cabecera Alimentador', 'Transferencia', 'Celda' o 'Línea')
Enterprise_PPD11 = '''TIPOUSO IS NULL OR (TIPOUSO NOT IN ('Cabecera Alimentador', 'Transferencia','Celda') 
                AND TIPOUSO NOT LIKE 'L_nea')'''

# Protección dinámica con orden de trabajo que contiene letras (SISTOT)
Enterprise_PPD12 = Enterprise_ot_Sistot

# ==============================================================================
# QUERIES PARA CAPA "PUESTO REGULADOR DE TENSIÓN"
# ==============================================================================

# Regulador sin tipo de control o con valor no válido
Enterprise_PRT08 = "control IS NULL OR control NOT IN ( 'Manual' , 'Telecomandado')"

# Regulador sin código de estructura o con código que no empieza con 'EC'
Enterprise_PRT09 = "CODIGOESTRUCTURA is null OR CODIGOESTRUCTURA NOT LIKE ('EC%')"

# Regulador con orden de trabajo que contiene letras (SISTOT)
Enterprise_PRT10 = Enterprise_ot_Sistot

# ==============================================================================
# QUERIES PARA CAPA "PUESTO SECCIONADOR CUCHILLA"
# ==============================================================================

# Seccionador sin código estructura ('SPT' o 'SPR'), sin TIPOUSO o con valor no válido
Enterprise_PSC08 = '''CODIGOESTRUCTURA IS NULL OR (CODIGOESTRUCTURA NOT LIKE ('SPT%') AND CODIGOESTRUCTURA NOT LIKE ('SPR%')) 
                OR TIPOUSO IS NULL OR (TIPOUSO NOT IN ('Transferencia','Celda') AND TIPOUSO NOT LIKE 'L_nea')'''

# Seccionador con alimentador asignado pero con ENABLED = 0 (deshabilitado)
Enterprise_PSC11 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Seccionador con orden de trabajo que contiene letras (SISTOT)
Enterprise_PSC12 = Enterprise_ot_Sistot

# Seccionador sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_PSC13 = Enterprise_ConsistenciaProvCantParr

# Seccionador sin Provincia, Cantón o Parroquia
Enterprise_PSC14 = Enterprise_ProvCantParr

# Seccionador cuyo código de estructura no corresponde a la cantidad de fases:
# - Monofásico (1,2,4): estructura debe contener '1F'
# - Bifásico (3,5,6): estructura debe contener '2F'
# - Trifásico (7): estructura debe contener '3F'
Enterprise_PSC15 = '''faseconexion in (1,2,4) AND codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionador.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%1F%') OR 
                faseconexion in (3,5,6) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionador.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%2F%') OR 
                faseconexion in (7) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionador.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%3F%')'''

# ==============================================================================
# QUERIES PARA CAPA "PUESTO SECCIONADOR FUSIBLE"
# ==============================================================================

# Seccionador fusible sin corriente nominal
Enterprise_PSF09 = "CORRIENTE IS NULL"

# Seccionador fusible sin código estructura o con código que no empieza con 'SPT' ni 'SPR'
Enterprise_PSF10 = "CODIGOESTRUCTURA IS NULL OR (CODIGOESTRUCTURA NOT LIKE ('SPT%') AND CODIGOESTRUCTURA NOT LIKE ('SPR%'))"

# Seccionador fusible con alimentador pero con ENABLED = 0
Enterprise_PSF11 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Tirafusible mal ingresado:
# - Monofásico (1,2,4): no debe tener separador ';' (una sola tira)
# - Bifásico/Trifásico: debe tener separador ';' (varias tiras)
Enterprise_PSF12 = '''FASECONEXION IN (1,2,4) AND TIRAFUSIBLE LIKE('%;%') OR FASECONEXION NOT IN (1,2,4) 
                AND TIRAFUSIBLE NOT LIKE('%;%')'''

# Seccionador fusible monofásico (1,2,4) con cantidad de unidades de fusible diferente de 1
Enterprise_PSF13 = '''globalid IN (SELECT uf.puestosecfusibleglobalid FROM SIGELEC.unidadfusible UF 
                GROUP BY uf.puestosecfusibleglobalid HAVING  COUNT(*)<>1) 
                AND sigelec.puestoseccionadorfusible.FASECONEXION IN (1,2,4) 
                AND alimentadorid is not null'''

# Seccionador fusible bifásico (5,3,6) con cantidad de unidades de fusible diferente de 2
Enterprise_PSF14 = '''globalid IN (SELECT uf.puestosecfusibleglobalid FROM SIGELEC.unidadfusible UF 
                GROUP BY uf.puestosecfusibleglobalid HAVING COUNT(*)<>2) 
                AND sigelec.puestoseccionadorfusible.FASECONEXION IN (5,3,6) 
                AND alimentadorid is not null'''

# Seccionador fusible trifásico (7) con cantidad de unidades de fusible diferente de 3
Enterprise_PSF15 = '''globalid IN (SELECT uf.puestosecfusibleglobalid FROM SIGELEC.unidadfusible UF 
                GROUP BY uf.puestosecfusibleglobalid HAVING COUNT(*)<>3) 
                AND sigelec.puestoseccionadorfusible.FASECONEXION IN (7) 
                AND alimentadorid is not null'''

# Seccionador fusible sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_PSF16 = Enterprise_ConsistenciaProvCantParr

# Seccionador fusible sin Provincia, Cantón o Parroquia
Enterprise_PSF17 = Enterprise_ProvCantParr

# Seccionador fusible cuyo código de estructura no corresponde a la cantidad de fases
# (misma lógica que PSC15 pero para la tabla puestoseccionadorfusible)
Enterprise_PSF18 = '''faseconexion in (1,2,4) AND codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionadorfusible.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%1F%') OR 
                faseconexion in (3,5,6) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionadorfusible.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%2F%') OR 
                faseconexion in (7) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.puestoseccionadorfusible.codigoestructura = CE.codigoestructura AND CE.DESCRIPCIONLARGA not like '%3F%')'''

# ==============================================================================
# QUERIES PARA CAPA "PUESTO TRANSFORMADOR DE DISTRIBUCIÓN"
# ==============================================================================

# Transformadores con CircuitSourceGUID repetido (más de un trafo con el mismo circuito)
Enterprise_PTD21 = '''circuitsourceguid in (select circuitsourceguid from SIGELEC.PUESTOTRANSFDISTRIBUCION t 
                group by t.circuitsourceguid having count (*) > 1 )'''

# Trafos (no alumbrado, tipo <> 2) con más de 100 luminarias asociadas
# Excluye los marcados con COMENTARIOS = 'NOAPLICA'
Enterprise_PTD22 = '''(tipo not in (2) and CircuitSourceGUID in (select l.PARENTCIRCUITSOURCEGUID from SIGELEC.LUMINARIA l 
                group by l.PARENTCIRCUITSOURCEGUID having count(*) > 100)) AND COMENTARIOS NOT IN ('NOAPLICA')'''

# Trafos con cargabilidad nula, mayor a 100% o igual a 0, y con más de 100 puntos de carga
Enterprise_PTD23 = '''(CARGABILIDAD IS NULL OR CARGABILIDAD >100 OR CARGABILIDAD =0) AND CircuitSourceGUID in 
                (select l.PARENTCIRCUITSOURCEGUID from SIGELEC.PUNTOCARGA l 
                group by l.PARENTCIRCUITSOURCEGUID having count(*) > 100) '''

# Trafos con tramos BT aéreos relacionados pero con alimentador diferente al del trafo
Enterprise_PTD24 = '''CIRCUITSOURCEGUID IN (SELECT  TB.PARENTCIRCUITSOURCEGUID FROM SIGELEC.TramoBajaTensionAereo TB 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.alimentadorid <> TB.alimentadorid)'''

# Trafos con tramos BT subterráneos relacionados pero con alimentador diferente al del trafo
Enterprise_PTD25 = '''CIRCUITSOURCEGUID IN (SELECT TB.PARENTCIRCUITSOURCEGUID FROM SIGELEC.TramoBajaTensionSubterraneo TB 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.alimentadorid <> TB.alimentadorid)'''

# Trafos con TIPORED nulo o no válido (debe ser 'Abierta', 'Preensamblada', 'Mixta',
# 'Subterranea', 'MultiAluminio' o 'Antihurto')
# Excluye trafos tipo 5,6 (distribución especial) y deshabilitados
Enterprise_PTD27 = '''TIPORED IS NULL OR TIPORED NOT IN ('Abierta', 'Preensamblada','Mixta','Subterranea','MultiAluminio', 
                'Antihurto') AND (TIPO NOT IN ( 5 ,6) or TIPO is null) and (enabled not in (0) or ENABLED is null)'''

# Trafos con TIPO nulo o fuera de los valores válidos (1-6)
Enterprise_PTD28 = "TIPO IS NULL OR TIPO NOT IN ('1', '2','3','4','5','6')"

# Trafos con cargabilidad mayor a 200% (sobrecarga severa)
Enterprise_PTD30 = "CARGABILIDAD > 200"

# Trafos (no bancos) cuyo código de estructura del puesto difiere de la unidad
Enterprise_PTD31 = '''subtipo in (1,2,3,4,5,6,7,8,13,14,15,16) and 
                GLOBALID IN (SELECT U.PUESTOTRANSFDISTGLOBALID FROM SIGELEC.UNIDADTRANSFDISTRIBUCION U 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.codigoestructura <> U.codigoestructura)'''

# Trafos cuya potencia (kVA) difiere de la potencia del catálogo de estructuras
Enterprise_PTD32 = '''subtipo in (1,2,3,4,5,6,7,8,13,14,15,16) and 
                CODIGOESTRUCTURA IN (SELECT CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.POTENCIAKVA <> CE.POTENCIA)'''

# Trafos de alumbrado (tipo 2) con más de 1 punto de carga (deberían tener solo 1)
Enterprise_PTD33 = '''tipo in (2) and CircuitSourceGUID in (select l.PARENTCIRCUITSOURCEGUID from SIGELEC.PUNTOCARGA l 
                group by l.PARENTCIRCUITSOURCEGUID having count(*) > 1)'''

# Trafos cuyo TIPO en el puesto difiere del TIPO en la unidad
Enterprise_PTD34 = '''subtipo in (1,2,3,4,5,6,7,8,13,14,15,16) and 
                GLOBALID IN (SELECT U.PUESTOTRANSFDISTGLOBALID FROM SIGELEC.UNIDADTRANSFDISTRIBUCION U 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.TIPO <> U.TIPO)'''

# Trafos cuyo voltaje secundario del puesto difiere del de la unidad
Enterprise_PTD35 = '''subtipo in (1,2,3,4,5,6,7,8,13,14,15,16) and 
                GLOBALID IN (SELECT U.PUESTOTRANSFDISTGLOBALID FROM SIGELEC.UNIDADTRANSFDISTRIBUCION U 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.VOLTAJESECUNDARIO <> u.VOLTAJESECUNDARIO)'''

# Trafos cuyo código de estructura no corresponde al subtipo:
# - Subtipo 1,2 (1F convencional): estructura debe contener '1F'
# - Subtipo 3,4 (Padmounted): estructura debe contener 'Padmounted'
# - Subtipo 5,6,7,8 (3F): estructura debe contener '3F'
# - Subtipo 9,10,11,12 (Banco): estructura debe contener 'Banco'
# - Subtipo 13,14,15,16 (2F): estructura debe contener '2F'
Enterprise_PTD36 = '''(subtipo in (1,2) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%1F%')) OR 
                (subtipo in (3,4) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%Padmounted%')) OR 
                (subtipo in (5,6,7,8) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%3F%')) OR 
                (subtipo in (9,10,11,12) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%Banco%')) OR 
                (subtipo in (13,14,15,16) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%2F%')) '''

# Trafos con más de 1 punto de carga totalizador (solo debe haber 1 totalizador por trafo)
Enterprise_PTD37 = '''CircuitSourceGUID in (select pc.PARENTCIRCUITSOURCEGUID from SIGELEC.PUNTOCARGA pc 
                where pc.totalizador = 'S' group by pc.PARENTCIRCUITSOURCEGUID having count(*) > 1) '''

# Trafos con orden de trabajo que contiene letras (SISTOT)
Enterprise_PTD38 = Enterprise_ot_Sistot

# Trafos donde Provincia, Cantón o Parroquia difieren entre el puesto y la unidad
Enterprise_PTD39 = '''GLOBALID IN (SELECT U.PUESTOTRANSFDISTGLOBALID FROM SIGELEC.UNIDADTRANSFDISTRIBUCION U 
                WHERE SIGELEC.PUESTOTRANSFDISTRIBUCION.GLOBALID= U.PUESTOTRANSFDISTGLOBALID AND 
                (SIGELEC.PUESTOTRANSFDISTRIBUCION.PARROQUIA <> U.PARROQUIA OR 
                SIGELEC.PUESTOTRANSFDISTRIBUCION.PROVINCIA <> U.PROVINCIA OR 
                SIGELEC.PUESTOTRANSFDISTRIBUCION.CANTON <> U.CANTON))'''

# Trafos cuyo alimentador pertenece a una subestación de subtipo 3 (particular)
# pero la propiedad no es 'PARTICULAR' (excluye subestación '17LP18')
Enterprise_PTD40 = '''PROPIEDAD<>'PARTICULAR' AND SUBSTR(ALIMENTADORID,1,6) IN (SELECT S.NOMBRE FROM SIGELEC.SUBESTACION S 
                WHERE S.SUBTIPO=3 AND S.NOMBRE<>'17LP18')'''

# Trafos donde MIGUID es nulo o no coincide con GLOBALID (integridad de migración)
Enterprise_PTD41 = '''MIGUID IS NULL OR GLOBALID <> MIGUID'''

# Trafos convencionales (subtipo aéreo: 1,5,9,11,13) sin poste asociado
Enterprise_PTD42 = '''SUBTIPO IN ( 1,5,9,11,13) AND ESTRUCTURASOPORTEGLOBALID IS NULL'''

# Trafos que tienen luminarias medidas (BAJOMEDICION=1) pero no tienen
# un punto de carga de tipo alumbrado (subtipo 10) asociado
Enterprise_PTD43 = '''EXISTS (
                        SELECT 1
                        FROM SIGELEC.Luminaria L
                        WHERE L.PARENTCIRCUITSOURCEGUID = SIGELEC.PuestoTransfDistribucion.CIRCUITSOURCEGUID
                        AND L.BAJOMEDICION = 1)
                AND NOT EXISTS (
                        SELECT 1
                        FROM SIGELEC.PuntoCarga PC
                        WHERE PC.PARENTCIRCUITSOURCEGUID = SIGELEC.PuestoTransfDistribucion.CIRCUITSOURCEGUID
                        AND PC.SUBTIPO = '10')'''

# Trafos sin total de clientes o total de luminarias calculado
Enterprise_PTD44 = '''TOTALCLIENTES IS NULL OR TOTALLUMINARIAS IS NULL'''

# ==============================================================================
# QUERIES PARA CAPA "PUNTO DE CARGA"
# ==============================================================================

# Puntos de carga con más de 100 conexiones de consumidor (posible error de carga masiva)
Enterprise_PC10 = '''globalid in (select l.puntocargaglobalid from SIGELEC.conexionconsumidor l 
                group by l.puntocargaglobalid having count(*) > 100)'''

# Puntos de carga asociados a más de 1 transformador (CIRCUITSOURCEGUID repetido en trafo)
Enterprise_PC11 = '''PARENTCIRCUITSOURCEGUID in (select l.CIRCUITSOURCEGUID from SIGELEC.puestotransfdistribucion l 
                group by l.CIRCUITSOURCEGUID having count(*) > 1)'''

# Puntos de carga con alimentador asignado pero ENABLED = 0 (deshabilitado)
Enterprise_PC12 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Puntos de carga cuyo alimentador difiere del alimentador de su transformador asociado
Enterprise_PC13 = '''parentcircuitsourceguid IN (SELECT TD.circuitsourceguid FROM SIGELEC.PUESTOTRANSFDISTRIBUCION TD 
                WHERE sigelec.puntocarga.alimentadorid <> TD.alimentadorid)'''

# Puntos de carga totalizadores ('S') con más de 1 conexión de consumidor
# (un totalizador debería tener solo 1 conexión)
Enterprise_PC14 = '''totalizador = 'S' and GLOBALID in (select l.PUNTOCARGAGLOBALID from SIGELEC.CONEXIONCONSUMIDOR l 
                group by l.PUNTOCARGAGLOBALID having count(*) > 1)'''

# Puntos de carga totalizadores cuyo consumidor tiene tarifa de uso propio o alumbrado
# (TP, TE, RP, RD) - excluyendo ciertos RUCs de empresa
Enterprise_PC16 = '''TOTALIZADOR= 'S' AND GLOBALID IN (SELECT CC.PUNTOCARGAGLOBALID FROM SIGELEC.CONEXIONCONSUMIDOR CC 
                WHERE CC.CODIGOUNICO IN(SELECT AT.CODIGOUNICO FROM SIGELEC.ATRIBUTOSCONSUMIDOR AT 
                WHERE AT.USOCOD in ('TP','TE','RP','RD') AND at.IDCCEDRUC NOT IN ('0968599020001','0990135657001',
                '0992598468001', '0968584420001', '1090051721001', '1234567897', '0968599020000', 
                '0968584420000','0990021007001')))'''

# Puntos de carga con orden de trabajo que contiene letras (SISTOT)
Enterprise_PC17 = Enterprise_ot_Sistot

# Puntos de carga cuyas coordenadas de SHAPE difieren de COORD_X / COORD_Y
# (coordenadas desactualizadas después de una edición geográfica)
Enterprise_PC18 = "ROUND(SDE.ST_X(SHAPE),0)<>ROUND(COORD_X,0) OR ROUND(SDE.ST_Y(SHAPE),0)<>ROUND(COORD_Y,0)"

# Puntos de carga donde Provincia, Cantón o Parroquia difieren de su conexión consumidor
Enterprise_PC19 = '''GLOBALID IN (SELECT U.PUNTOCARGAGLOBALID FROM SIGELEC.CONEXIONCONSUMIDOR U 
                WHERE sigelec.puntocarga.GLOBALID= U.PUNTOCARGAGLOBALID AND (SIGELEC.PUNTOCARGA.PARROQUIA <> U.PARROQUIA 
                OR SIGELEC.PUNTOCARGA.PROVINCIA <> U.PROVINCIA OR SIGELEC.PUNTOCARGA.CANTON <> U.CANTON))'''

# Puntos de carga de alto voltaje (subtipo 9) sin nombre de subestación
# o con nombre de longitud diferente a 6 caracteres
Enterprise_PC20 = "SUBTIPO = 9 AND (ALIMENTADOR IS NULL OR LENGTH(ALIMENTADOR) <> 6)"

# Puntos de carga subtipo 8 (MT) sin GLOBALID de acometida (TRAMOGLOBALID)
# que tienen alimentador asignado
Enterprise_PC21 = '''TRAMOGLOBALID IS NULL AND SUBTIPO = 8 AND ALIMENTADORID IS NOT NULL'''

# ==============================================================================
# QUERIES PARA CAPA "POSTE" (Estructura Soporte)
# ==============================================================================

# Postes con código de elemento repetido (excepto 'M04000000' que es código genérico)
Enterprise_POS01 = '''codigoelemento not in ('M04000000') and 
                codigoelemento in (select t.codigoelemento from sigelec.estructurasoporte t group by t.CODIGOELEMENTO 
                having count(*) > 1 )'''

# Postes sin código de estructura o con código que no empieza con 'POO' ni 'TOO'
Enterprise_POS02 = "CODIGOESTRUCTURA IS NULL or (CODIGOESTRUCTURA not like ('POO%')  and CODIGOESTRUCTURA not like ('TOO%'))"

# Postes sin tipo de uso o con tipo de uso fuera del rango válido (1-10)
Enterprise_POS03 = "tipousoposte IS NULL  or tipousoposte not in ( 1,2,3,4,5,6,7,8,9,10)"

# Postes sin placa (código de elemento nulo)
Enterprise_POS04 = "codigoelemento is null"

# Postes con código de empresa incorrecto
Enterprise_POS05 = Enterprise_CodigoEmpresa

# Postes sin Provincia, Cantón o Parroquia
Enterprise_POS06 = Enterprise_ProvCantParr

# Postes sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_POS07 = Enterprise_ConsistenciaProvCantParr

# Postes cuyo código de estructura no corresponde al subtipo (material):
# - Subtipo 1 (Hormigón): estructura debe contener 'Hormigón'
# - Subtipo 2 (Madera): estructura debe contener 'Madera'
# - Subtipo 3 (Plástico): estructura debe contener 'Plástico'
# - Subtipo 4 (Metálico): estructura debe contener 'Metálico'
# - Subtipo 6 (Torre): estructura debe contener 'Torre'
Enterprise_POS08 = '''(subtipo in (1) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CE.DESCRIPCIONLARGA not like '%Hormig_n%')) OR 
                (subtipo in (2) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE  
                WHERE CE.DESCRIPCIONLARGA not like '%Madera%')) OR 
                (subtipo in (3) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE  
                WHERE CE.DESCRIPCIONLARGA not like '%Pl_stico%')) OR 
                (subtipo in (4) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE  
                WHERE CE.DESCRIPCIONLARGA not like '%Met_lico%')) OR 
                (subtipo in (6) and codigoestructura IN (SELECT CE.codigoestructura FROM SIGELEC.CATALOGOESTRUCTURA CE  
                WHERE CE.DESCRIPCIONLARGA not like '%Torre%'))'''

# Postes con orden de trabajo que contiene letras (SISTOT)
Enterprise_POS09 = Enterprise_ot_Sistot

# Postes (no madera, metálico, especial) sin estructura en poste relacionada
# y con tipo de uso diferente de 1,5,6,8,9,10
Enterprise_POS10 = '''SUBTIPO NOT IN ( 2,4,5 ) AND (TIPOUSOPOSTE NOT IN (1,5,6,8,9,10)) AND 
                (GLOBALID NOT IN (select c.ESTRUCTURASOPORTEGLOBALID FROM sigelec.estructuraenposte c WHERE c.ESTRUCTURASOPORTEGLOBALID IS NOT NULL))'''

# Postes con propiedad no válida (debe ser 'COD_EMPRESA' o 'PARTICULAR')
Enterprise_POS11 = "PROPIEDAD NOT IN ('COD_EMPRESA', 'PARTICULAR')"

# Postes donde MIGUID es nulo o no coincide con GLOBALID (integridad de migración)
Enterprise_POS12 = "MIGUID IS NULL OR GLOBALID <> MIGUID"

# Postes con coordenadas desactualizadas (SHAPE vs COORD_X/COORD_Y)
Enterprise_POS13 = "ROUND(SDE.ST_X(SHAPE),0)<>ROUND(COORD_X,0) OR ROUND(SDE.ST_Y(SHAPE),0)<>ROUND(COORD_Y,0)"

# ==============================================================================
# QUERIES PARA CAPA "LUMINARIA"
# ==============================================================================

# Luminarias con fuente de energía renovable pero con alimentador asignado
# (fotovoltaicas no deberían tener alimentador de red convencional)
Enterprise_LUM07 = "(FUENTEENERGIA IN ('Fotovoltaico', 'Biomasa', 'E_lica', 'Mini Hidr_ulica') AND ALIMENTADORID IS NOT NULL)"

# Luminarias sin potencia, con potencia <= 0 o >= 5000W (valores no realistas)
Enterprise_LUM08 = "potencia is null or potencia <= 0 or potencia >= 5000"

# Luminarias con campos de clasificación o propiedad nulos/no válidos:
# - BAJOMEDICION debe ser 0 o 1
# - PROPIEDAD debe ser 'Distribuidora', 'Municipal' o 'Particular'
# - CLASIFICACION_AP debe ser 'General', 'Ornamental', 'Intervenido' o 'Escenario Deportivo'
# - FUENTEENERGIA debe tener un valor válido
# - No puede ser 'Distribuidora' + 'Ornamental' simultáneamente
Enterprise_LUM09 = '''bajomedicion is null  or bajomedicion not in (0,1) or propiedad is null or 
                propiedad not in ('Distribuidora','Municipal','Particular') or clasificacion_ap is null or 
                clasificacion_ap not in ('General', 'Ornamental','Intervenido','Escenario Deportivo') 
                or fuenteenergia is null or FUENTEENERGIA not in ('Fotovoltaico', 'Biomasa', 'E_lica', 
                'Mini Hidr_ulica', 'Convencional') OR ((PROPIEDAD = 'Distribuidora' ) AND 
                CLASIFICACION_AP = 'Ornamental' )'''

# Luminarias con código de estructura de 120V (listado específico) pero con
# secuencia de fase diferente de 'a', 'b', 'c' (deberían ser monofásicas)
Enterprise_LUM12 = '''CODIGOESTRUCTURA in ('AOC0001','APO0131','APO0238','APO0240','APO0242','APO0243','APO0302','APO0303', 
                'APO0309','APO0310','APO0322','APO0323','APO0329','APO0330','APO0628','APO0629','APO0630','APO0720', 
                'APO0721','APO0746','APO0747','APO0751') and SECUENCIAFASE NOT IN ('a','b','c')'''

# Luminarias con alimentador pero con ENABLED = 0 (deshabilitada)
Enterprise_LUM13 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Luminarias con relación incorrecta entre fase, secuencia de fase y circuitos:
# - Fases 1,5 (C, AC): secuencia debe ser 'a','ac','c' y circuitos 'A','AC','C','F1','F12','F2'
# - Fases 2,3 (B, BC): secuencia debe ser 'b','bc','c' y circuitos 'B','BC','C','F1','F12','F2'
# - Fases 4,6 (A, AB): secuencia debe ser 'a','ab','b' y circuitos 'A','AB','B','F1','F12','F2'
Enterprise_LUM14 = '''FASECONEXION in (1,5) AND (SECUENCIAFASE not in ('a', 'ac', 'c') or 
                CIRCUITOS not in ('A', 'AC', 'C', 'F1', 'F12', 'F2')) OR FASECONEXION in (2,3) AND 
                (SECUENCIAFASE not in ('b', 'bc', 'c') or CIRCUITOS not in ('B', 'BC', 'C', 'F1', 'F12', 'F2')) 
                OR FASECONEXION in (4,6) AND (SECUENCIAFASE not in ('a', 'ab', 'b') or 
                CIRCUITOS not in ('A', 'AB', 'B', 'F1', 'F12', 'F2'))'''

# Luminarias con circuitos F1, F12, F2 (monofásico) conectadas a trafos que
# NO son monofásicos ni bancos 2F (subtipos distintos de 1,2,3,4,9,10)
Enterprise_LUM15 = '''CIRCUITOS in ('F1', 'F12', 'F2') AND PARENTCIRCUITSOURCEGUID IN 
                (select t.CIRCUITSOURCEGUID FROM sigelec.puestotransfdistribucion t 
                WHERE t.CIRCUITSOURCEGUID IS NOT NULL AND t.SUBTIPO NOT IN ( 1,2,3,4,9,10))'''

# Luminarias con circuitos diferentes de F1, F12, F2 conectadas a trafos monofásicos (1,2,3,4)
Enterprise_LUM16 = '''CIRCUITOS not in ('F1', 'F12', 'F2') AND PARENTCIRCUITSOURCEGUID  IN 
                (select t.CIRCUITSOURCEGUID   FROM sigelec.puestotransfdistribucion t 
                WHERE t.CIRCUITSOURCEGUID IS NOT NULL AND t.SUBTIPO IN ( 1,2,3,4))'''

# Luminarias cuya potencia difiere de la potencia del catálogo de estructuras
# (excluye ciertos códigos especiales)
Enterprise_LUM17 = '''codigoestructura not in ('AOD0145','AOD0090','APO0701','AOD0032','AOD0145') AND 
                CODIGOESTRUCTURA IN (SELECT CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE sigelec.luminaria.potencia <> CE.POTENCIA)'''

# Luminarias cuyo alimentador difiere del alimentador de su transformador asociado
Enterprise_LUM18 = '''parentcircuitsourceguid IN (SELECT TD.circuitsourceguid FROM SIGELEC.PUESTOTRANSFDISTRIBUCION TD 
                WHERE sigelec.luminaria.alimentadorid <> TD.alimentadorid)'''

# Luminarias cuyo código de estructura no corresponde al subtipo (tecnología):
# - Subtipos 1,2,7 (Mercurio - Hg)
# - Subtipos 3,4,6 (Sodio - Na)
# - Subtipos 5,12 (Led)
# - Subtipos 10,11 (Metal Halide - MH)
# - Subtipo 9 (Inducción)
Enterprise_LUM19 = '''(subtipo in (1,2,7) and codigoestructura IN (SELECT CE.codigoestructura 
                FROM SIGELEC.CATALOGOESTRUCTURA CE WHERE CE.DESCRIPCIONLARGA not like '%Hg%')) OR 
                (subtipo in (3,4,6) and codigoestructura IN (SELECT CE.codigoestructura 
                FROM SIGELEC.CATALOGOESTRUCTURA CE WHERE CE.DESCRIPCIONLARGA not like '%Na%')) OR 
                (subtipo in (5,12) and codigoestructura IN (SELECT CE.codigoestructura 
                FROM SIGELEC.CATALOGOESTRUCTURA CE WHERE CE.DESCRIPCIONLARGA not like '%Led%')) OR 
                (subtipo in (10,11) and codigoestructura IN (SELECT CE.codigoestructura 
                FROM SIGELEC.CATALOGOESTRUCTURA CE WHERE CE.DESCRIPCIONLARGA not like '%MH%')) OR 
                (subtipo in (9) and codigoestructura IN (SELECT CE.codigoestructura 
                FROM SIGELEC.CATALOGOESTRUCTURA CE WHERE CE.DESCRIPCIONLARGA not like '%Induccion%')) '''

# Luminarias con orden de trabajo que contiene letras (SISTOT)
Enterprise_LUM20 = Enterprise_ot_Sistot

# Luminarias de propiedad 'Distribuidora' con potencia fuera del rango 60-600W
Enterprise_LUM21 = "(potencia <=60 or potencia >=600) and propiedad in ('Distribuidora')"

# Luminarias en alimentador particular (subestación subtipo 3) pero con propiedad
# diferente de 'Distribuidora' (inconsistencia de propiedad)
Enterprise_LUM22 = '''GLOBALID IN (SELECT L.GLOBALID
                FROM SIGELEC.LUMINARIA L 
                INNER JOIN SIGELEC.SUBESTACION S 
                ON SUBSTR(L.ALIMENTADORID, 1, 6) = S.NOMBRE
                WHERE S.SUBTIPO = 3 
                AND L.PROPIEDAD <> 'Distribuidora' 
                AND L.ALIMENTADORID <> '17LP180T11'
                AND S.NUMEROSUBESTACION <> '12P015'
                )'''

# Luminarias donde MIGUID es nulo o no coincide con GLOBALID (integridad de migración)
Enterprise_LUM23 = '''MIGUID IS NULL OR GLOBALID <> MIGUID'''

# Luminarias con alimentador, sin poste relacionado, que no son 'Ornamental'
# y cuya estructura no es de tipo fachada ni piso (requieren poste)
Enterprise_LUM24 = '''ALIMENTADORID IS NOT NULL 
                AND ESTRUCTURASOPORTEGLOBALID IS NULL
                AND CLASIFICACION_AP <> 'Ornamental'
                AND GLOBALID IN( SELECT L.GLOBALID 
                FROM SIGELEC.LUMINARIA L
                INNER JOIN SIGELEC.CATALOGOESTRUCTURA C
                ON L.CODIGOESTRUCTURA = C.CODIGOESTRUCTURA
                WHERE
                C.DESCRIPCIONLARGA NOT LIKE '%fachada%'
                AND C.DESCRIPCIONLARGA NOT LIKE '%Fachada%'
                AND C.DESCRIPCIONLARGA NOT LIKE '%piso%'
                AND C.DESCRIPCIONLARGA NOT LIKE '%Piso%'
                )
'''

# Luminarias con doble nivel de potencia (tipo 'D') incorrectas:
# - Registradas antes de 2020 con tipo D, o
# - Subtipo diferente de 3,4 (Na) pero con tipo D en catálogo
Enterprise_LUM25 = '''GLOBALID IN(SELECT L.GLOBALID
                FROM SIGELEC.LUMINARIA L
                INNER JOIN SIGELEC.CATALOGOESTRUCTURA C
                ON L.CODIGOESTRUCTURA = C.CODIGOESTRUCTURA
                WHERE 
                (C.TIPO = 'D' AND TO_CHAR(L.FECHAREGISTRO, 'YYYY') < '2020') OR
                (L.SUBTIPO NOT IN (3, 4) AND C.TIPO = 'D')
                )'''

# ==============================================================================
# QUERIES PARA CAPA "SEMÁFORO"
# ==============================================================================

# Semáforos con horas de funcionamiento o días de funcionamiento nulos o fuera de rango
# (horas > 24, días > 100, o suma de horas func1 + func2 > 24)
Enterprise_SEM07 = '''horasfunc1 is null or diasfuncmes is null or to_number(horasfunc1)> 24 or 
                to_number(diasfuncmes)> 100 or ((to_number(horasfunc1)+ to_number(horasfunc2)) > 24)'''

# Semáforos con alimentador pero con ENABLED = 0
Enterprise_SEM08 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Semáforos con relación incorrecta entre fase, secuencia de fase y circuitos
# (misma lógica que luminarias LUM14)
Enterprise_SEM09 = '''FASECONEXION in (1,5) AND (SECUENCIAFASE not in ('a', 'ac', 'c') or 
                CIRCUITOS not in ('A', 'AC', 'C', 'F1', 'F12', 'F2')) OR FASECONEXION in (2,3) AND 
                (SECUENCIAFASE not in ('b', 'bc', 'c') or CIRCUITOS not in ('B', 'BC', 'C', 'F1', 'F12', 'F2')) 
                OR FASECONEXION in (4,6) AND (SECUENCIAFASE not in ('a', 'ab', 'b') or 
                CIRCUITOS not in ('A', 'AB', 'B', 'F1', 'F12', 'F2'))'''

# Semáforos con circuitos F1, F12, F2 conectados a trafos no monofásicos
Enterprise_SEM10 = '''CIRCUITOS in ('F1', 'F12', 'F2') AND PARENTCIRCUITSOURCEGUID IN (select t.CIRCUITSOURCEGUID 
                FROM sigelec.puestotransfdistribucion t WHERE t.CIRCUITSOURCEGUID IS NOT NULL 
                AND t.SUBTIPO NOT IN ( 1,2,3,4,9,10))'''

# Semáforos con circuitos diferentes de F1, F12, F2 conectados a trafos monofásicos
Enterprise_SEM11 = '''CIRCUITOS not in ('F1', 'F12', 'F2') 
                AND PARENTCIRCUITSOURCEGUID IN (select t.CIRCUITSOURCEGUID FROM sigelec.puestotransfdistribucion t 
                WHERE t.CIRCUITSOURCEGUID IS NOT NULL AND t.SUBTIPO IN ( 1,2,3,4))'''

# Semáforos sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_SEM12 = Enterprise_ConsistenciaProvCantParr 

# Semáforos sin Provincia, Cantón o Parroquia
Enterprise_SEM13 = Enterprise_ProvCantParr

# ==============================================================================
# QUERIES PARA TABLA "CIRCUITO FUENTE"
# ==============================================================================

# Circuitos fuente con código de empresa incorrecto
Enterprise_CF00 = Enterprise_CodigoEmpresa

# Circuitos fuente donde el IDSUBESTACION no coincide con los primeros 6 caracteres
# del CODIGOALIMENTADOR
Enterprise_CF01 = "IDSUBESTACION <>SUBSTR(CODIGOALIMENTADOR,0,6)"

# Circuitos fuente sin zona de influencia definida
Enterprise_CF02 = "ZONAINFLUENCIA IS NULL"

# Alimentadores cuyo troncal MTA tiene más de 4 conductores de fase diferentes
# (sustituye al query "MTA_Troncal con mas de 4 conductores")
Enterprise_CFXX = '''CODIGOALIMENTADOR IN (SELECT MTA.ALIMENTADORID FROM SIGELEC.TRAMODISTRIBUCIONAEREO MTA WHERE
                MTA.RAMAL='Troncal' GROUP BY MTA.ALIMENTADORID HAVING COUNT (DISTINCT MTA.CODIGOCONDUCTORFASE)>3)'''

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD TRANSFORMADOR DE DISTRIBUCIÓN"
# ==============================================================================

# Unidades de transformador sin código de unidad (sticker nulo)
Enterprise_UTD11 = "codigounidad is null"

# Unidades con propiedad nula o diferente de 'PARTICULAR' y 'COD_EMPRESA'
Enterprise_UTD12 = "PROPIEDAD IS NULL  OR PROPIEDAD NOT  IN ('PARTICULAR', 'COD_EMPRESA')"

# Unidades con TIPO nulo o fuera de los valores válidos (1-6)
Enterprise_UTD13 = "TIPO IS NULL OR TIPO NOT IN ('1', '2','3','4','5','6') "

# Unidades sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_UTD14 = Enterprise_ConsistenciaProvCantParr

# Unidades con código de estructura que corresponde a 'Banco' en el catálogo
# (posible inconsistencia si la unidad no debería ser banco)
Enterprise_UTD15 = '''CODIGOESTRUCTURA IN ( SELECT CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE CODIGOESTRUCTURA = CE.CODIGOESTRUCTURA AND DESCRIPCIONLARGA LIKE '%Banco%')'''

# Unidades cuyo trafo pertenece a subestación particular (subtipo 3) pero
# la propiedad no es 'PARTICULAR'
Enterprise_UTD16 = '''PUESTOTRANSFDISTGLOBALID IN ( SELECT T.GLOBALID FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T 
                WHERE SUBSTR(ALIMENTADORID,1,6) IN (SELECT S.NOMBRE FROM SIGELEC.SUBESTACION S WHERE 
                S.SUBTIPO=3 AND S.NOMBRE<>'17LP18')) AND PROPIEDAD <> 'PARTICULAR' '''

# Unidades cuya propiedad difiere de la propiedad del puesto del transformador
Enterprise_UTD17 = '''PUESTOTRANSFDISTGLOBALID IN ( SELECT T.GLOBALID FROM SIGELEC.PUESTOTRANSFDISTRIBUCION T 
                WHERE PROPIEDAD <> T. PROPIEDAD) '''

# Unidades cuya potencia nominal difiere de la potencia del catálogo de estructuras
Enterprise_UTD18 = '''GLOBALID IN (SELECT UT.GLOBALID 
                FROM SIGELEC.UNIDADTRANSFDISTRIBUCION UT 
                INNER JOIN SIGELEC.CATALOGOESTRUCTURA CE 
                ON UT.CODIGOESTRUCTURA = CE.CODIGOESTRUCTURA 
                WHERE TO_NUMBER(REPLACE(UT.POTENCIANOMINAL, '.', ',')) <> CE.POTENCIA 
                )'''

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD REGULADOR"
# ==============================================================================

# Unidades de regulador con código ADMS repetido
Enterprise_URT06 = '''CODIGOADMS IN (SELECT t.codigoadms from SIGELEC.UNIDADREGULADORTENSION t 
                group by t.codigoadms having count (*)>1 )'''

# Unidades de regulador sin código de estructura o con código que no empieza con 'EC'
Enterprise_URT07 = "CODIGOESTRUCTURA IS NULL OR CODIGOESTRUCTURA NOT LIKE ('EC%')"

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD CAPACITOR"
# ==============================================================================

# Unidades de capacitor sin código de estructura o con código que no empieza con 'ECT'
Enterprise_UCAP06 = "CODIGOESTRUCTURA IS NULL OR CODIGOESTRUCTURA NOT LIKE ('ECT%')"

# ==============================================================================
# QUERIES PARA TABLA "CONEXIÓN CONSUMIDOR"
# ==============================================================================

# Conexiones con código único lleno pero con novedad de baja (4, 5, 11)
# (si tiene novedad de baja, no debería tener código único activo)
Enterprise_CC08 = "(CODIGOUNICO IS not NULL AND NOVEDADES IN ( 4 , 5 , 11 ))"

# Conexiones sin GLOBALID del punto de carga (sin relación al punto de carga)
Enterprise_CC09 = "PUNTOCARGAGLOBALID IS NULL"

# Conexiones con código único que no empieza con '17' (código de empresa)
Enterprise_CC10 = '''CODIGOUNICO NOT LIKE '17%' '''

# ==============================================================================
# QUERIES PARA TABLA "ESTRUCTURA EN POSTE"
# ==============================================================================

# Estructuras en poste sin GLOBALID de poste asociado
Enterprise_ESP01 = "estructurasoporteglobalid is null"

# Estructuras en poste con código de empresa incorrecto
Enterprise_ESP02 = Enterprise_CodigoEmpresa

# Estructuras en poste sin código de estructura o con código que no empieza con 'ES'
Enterprise_ESP03 = "CODIGOESTRUCTURA IS NULL or CODIGOESTRUCTURA not like ('ES%')"

# Estructuras en poste sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_ESP04 = Enterprise_ConsistenciaProvCantParr

# Estructuras en poste sin Provincia, Cantón o Parroquia
Enterprise_ESP05 = Enterprise_ProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "TRAMOS BT" (Baja Tensión)
# ==============================================================================

# Tramos BT con relación incorrecta entre fase de conexión y alimentador INFO
# (misma validación que ADMS_FaseConexionAlimentadorINFO pero con formato de la empresa)
Enterprise_BT01 = '''(FASECONEXION = 1 AND (ALIMENTADORINFO NOT IN (4,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 2 AND (ALIMENTADORINFO NOT IN (2,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 3 AND (ALIMENTADORINFO NOT IN (6,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 4 AND (ALIMENTADORINFO NOT IN (1,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 5 AND (ALIMENTADORINFO NOT IN (5,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 6 AND (ALIMENTADORINFO NOT IN (3,0,8)  OR  ALIMENTADORINFO IS NULL)) 
                OR (FASECONEXION = 7 AND (ALIMENTADORINFO NOT IN (7,0,8)  OR  ALIMENTADORINFO IS NULL))'''

# Acometidas (subtipo 7,8,9) con longitud mayor a 500m (posible error geométrico)
Enterprise_BT02 = "SHAPE.LEN>500  and subtipo IN (7,8,9)"

# Tramos BT con código de empresa incorrecto
Enterprise_BT03 = Enterprise_CodigoEmpresa

# Tramos BT sin alimentador pero habilitados (ENABLED <> 0 o nulo)
Enterprise_BT04 = "ALIMENTADORID IS NULL AND (ENABLED NOT IN (0) OR ENABLED IS NULL)"

# Tramos BT con código de conductor de fase o neutro nulo, '000' o sin formato 'COO'
Enterprise_BT05 = '''CODIGOCONDUCTORFASE IS NULL OR (CODIGOCONDUCTORFASE = 'COO0000') OR (CODIGOCONDUCTORNEUTRO = 'COO0000') 
                OR CODIGOCONDUCTORFASE NOT LIKE ('COO%') OR CODIGOCONDUCTORNEUTRO NOT LIKE ('COO%')'''

# Tramos BT con voltaje nulo o fuera de los valores estándar de BT
Enterprise_BT06 = "voltaje IS NULL or voltaje not in (120,121,127,208,210,219,220,240,231,254,266,277,380,400,440,460,480)"

# Tramos BT con alimentador pero ENABLED = 0 (deshabilitado)
Enterprise_BT07 = "ALIMENTADORID IS NOT NULL AND ENABLED IN (0)"

# Tramos BT (NO acometidas, subtipo <> 7,8,9) con voltaje 240V:
# valida configuración de conductores y circuitos compatibles
Enterprise_BT08 = '''SUBTIPO NOT IN (7,8,9) and VOLTAJE in ('240') AND 
                (CONFIGURACIONCONDUCTORES not in ('12','13','14','22','23','24', '34') or 
                CIRCUITOS not in ( 'AB' , 'BC' , 'AC', 'ABC','F12'))'''

# Tramos BT (NO acometidas) con voltaje 208V o 220V: valida configuración y circuitos
Enterprise_BT09 = '''SUBTIPO NOT IN (7,8,9) and VOLTAJE in ('208', '220') AND 
                (CONFIGURACIONCONDUCTORES not in ('22','23', '24', '34') or 
                CIRCUITOS not in ( 'AB' , 'BC' , 'AC', 'ABC'))'''

# Tramos BT (NO acometidas) con voltaje 120V o 127V: valida configuración y circuitos
Enterprise_BT10 = '''SUBTIPO NOT IN (7,8,9) AND VOLTAJE in ('120', '127') AND (CONFIGURACIONCONDUCTORES not in ('12', '14') 
                or CIRCUITOS  not in ( 'A' , 'B' , 'C', 'F1', 'F2'))'''

# Tramos BT (NO acometidas) con voltaje 208V conectados a trafos que no son banco 3F (11,12)
Enterprise_BT11 = '''(VOLTAJE  IN ('208') AND SUBTIPO NOT IN (7,8,9) AND (PARENTCIRCUITSOURCEGUID IN 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO  NOT IN (11,12))))))'''

# Tramos BT (NO acometidas) con voltaje 120/240V conectados a trafos incompatibles
Enterprise_BT12 = '''(VOLTAJE  IN ('120', '240') AND  SUBTIPO NOT IN (7,8,9) 
                AND (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO  NOT IN (1,2,3,4,9,10,11,12))))))'''

# Tramos BT (NO acometidas) con voltaje 127/220V conectados a trafos incompatibles
Enterprise_BT13 = '''(VOLTAJE IN ('127', '220') AND SUBTIPO NOT IN (7,8,9) AND (PARENTCIRCUITSOURCEGUID IN 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO  NOT IN (5, 6, 7, 8, 13, 14, 15, 16))))))'''

# Tramos BT (NO acometidas) con config. conductores bifásica/trifásica (23,33,34)
# conectados a trafos monofásicos (1,2,3,4)
Enterprise_BT14 = '''(CONFIGURACIONCONDUCTORES in ('23','33','34') AND SUBTIPO NOT IN (7,8,9) 
                AND (PARENTCIRCUITSOURCEGUID IN (select  PD.CIRCUITSOURCEGUID  FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO   IN (1,2,3,4))))))'''

# Tramos BT (NO acometidas) con circuitos F1,F2,F12 conectados a bancos 2F
# cuya estructura no es banco paralelo
Enterprise_BT15 = '''(CIRCUITOS in ( 'F1' , 'F2' , 'F12') AND SUBTIPO NOT IN (7,8,9)) AND (PARENTCIRCUITSOURCEGUID IN 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE  (PD.SUBTIPO  IN (9,10) and PD.CODIGOESTRUCTURA in 
                (select  CE.CODIGOESTRUCTURA  FROM SIGELEC.CATALOGOESTRUCTURA CE 
                where (CE.DESCRIPCIONCORTA  not LIKE '1B%' and CE.DESCRIPCIONCORTA not LIKE '1V%')))))'''

# Tramos BT (NO acometidas) con circuitos F1,F2,F12 conectados a trafos trifásicos/bifásicos
Enterprise_BT16 = '''(CIRCUITOS in ( 'F1' , 'F2' , 'F12') AND SUBTIPO  NOT IN (7,8,9)) AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID  FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE ( PD.SUBTIPO  IN (5, 6, 7, 8, 11, 12, 13, 14, 15, 16)))) '''

# Tramos BT (NO acometidas) con circuitos multifásicos conectados a trafos monofásicos
Enterprise_BT17 = '''(CIRCUITOS in ( 'A' , 'B' , 'C', 'AB' , 'BC' , 'AC', 'ABC') AND SUBTIPO NOT IN (7,8,9) AND 
                ((PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO IN (1,2,3,4)))))))'''

# Tramos BT (NO acometidas) con código de conductor de fase no válido
Enterprise_BT18 = '''SUBTIPO NOT IN (7,8,9) AND ((CODIGOCONDUCTORFASE NOT LIKE  '%COO____%') OR 
                (CODIGOCONDUCTORFASE is null) or (CODIGOCONDUCTORFASE = ''))'''

# Tramos BT (NO acometidas) sin Provincia, Cantón o Parroquia
Enterprise_BT19 = "SUBTIPO NOT in (7, 8, 9 ) AND " + Enterprise_ProvCantParr

# Tramos BT (NO acometidas) con circuitos nulos o en minúsculas
Enterprise_BT20 = '''SUBTIPO  NOT IN (7,8,9)  AND ((CIRCUITOS IS NULL) OR (CIRCUITOS IN 
                ('a','b','c','ab','ac','bc','abc','f1','f2','f12')))'''

# Tramos BT (NO acometidas) sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_BT21 = "SUBTIPO  NOT IN (7,8,9) AND " + Enterprise_ConsistenciaProvCantParr

# Tramos BT con relación incorrecta entre fase, secuencia de fase y circuitos
# (incluye 'abc' como secuencia válida adicional respecto a luminarias)
Enterprise_BT22 = '''FASECONEXION in (1,5) AND (SECUENCIAFASE not in ('a', 'ac', 'c','abc') or 
                CIRCUITOS not in ('A', 'AC', 'C','ABC', 'F1', 'F12', 'F2')) OR FASECONEXION in (2,3) AND (SECUENCIAFASE 
                not in ('b', 'bc', 'c','abc') or CIRCUITOS not in ('B', 'BC', 'C','ABC', 'F1', 'F12', 'F2')) 
                OR FASECONEXION in (4,6) AND (SECUENCIAFASE not in ('a', 'ab', 'b','abc') or 
                CIRCUITOS not in ('A', 'AB', 'B','ABC', 'F1', 'F12', 'F2'))'''

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD FUSIBLE"
# ==============================================================================

# Unidades de fusible sin fase de conexión
Enterprise_UF01 = "FASECONEXION IS NULL"

# Unidades de fusible con capacidad mal ingresada (misma lógica que ADMS_PSF04
# pero para el campo CAPACIDAD en lugar de TIRAFUSIBLE)
Enterprise_UF02 = '''(CAPACIDAD NOT LIKE('%K') AND CAPACIDAD NOT LIKE('%H') AND CAPACIDAD NOT LIKE('%T') AND 
                CAPACIDAD NOT LIKE('%SF')) OR CAPACIDAD LIKE ('%,%') OR CAPACIDAD IS NULL OR CAPACIDAD LIKE ('% %') 
                OR CAPACIDAD = (' ')    OR CAPACIDAD = 'X'    OR CAPACIDAD = 'H'     OR CAPACIDAD = 'H;H' 
                OR CAPACIDAD = 'H;H;H'  OR CAPACIDAD = 'K'    OR CAPACIDAD = 'K;K'   OR CAPACIDAD = 'K;K;K' 
                OR CAPACIDAD = 'T'      OR CAPACIDAD = 'T;T'  OR CAPACIDAD = 'T;T;T' OR CAPACIDAD = 'SF' 
                OR CAPACIDAD = 'SF;SF'  OR CAPACIDAD = 'SF;SF;SF' '''

# ==============================================================================
# QUERIES PARA CAPA "SUBTRANSMISIÓN AÉREO"
# ==============================================================================

# Tramos de subtransmisión con código de empresa incorrecto
Enterprise_ST01 = Enterprise_CodigoEmpresa

# Tramos ST con código de conductor de fase o neutro nulo, '000' o sin formato 'COO'
Enterprise_ST02 = '''CODIGOCONDUCTORFASE IS NULL OR CODIGOCONDUCTORFASE = 'COO0000' OR (CODIGOCONDUCTORNEUTRO = 'COO0000') 
                OR CODIGOCONDUCTORFASE NOT LIKE ('COO%') OR CODIGOCONDUCTORNEUTRO NOT LIKE ('COO%')'''

# Tramos ST sin consistencia jerárquica entre Provincia, Cantón y Parroquia
Enterprise_ST03 = Enterprise_ConsistenciaProvCantParr

# Tramos ST con alimentador asignado (no deberían tener alimentador, son de subtransmisión)
Enterprise_ST04 = "ALIMENTADORID IS not NULL "

# Tramos ST sin nombre de línea (TEXTOETIQUETA nulo)
Enterprise_ST05 = "TEXTOETIQUETA IS NULL"

# ==============================================================================
# QUERIES PARA CAPA "SUBESTACIÓN"
# ==============================================================================

# Subestaciones con subtipo no válido (debe ser 2 o 3) o sin nombre
Enterprise_SUB01 = "subtipo not in (2,3)  or nombre is null"

# Subestaciones con código de empresa incorrecto
Enterprise_SUB02 = Enterprise_CodigoEmpresa

# Subestaciones de distribución (subtipo 2) sin transformador de potencia relacionado
# y cuyas observaciones no indican seccionamiento ni protección
Enterprise_SUB03 = '''(OBSERVACIONES NOT LIKE ('%SECCIONAMIENTO%') AND OBSERVACIONES NOT LIKE ('%PROTECCION%')) AND 
                (SUBTIPO = 2) AND GLOBALID not in (select PT.SUBESTACIONGLOBALID FROM SIGELEC.PUESTOTRANSFPOTENCIA PT 
                WHERE PT.SUBESTACIONGLOBALID  IS NOT NULL)'''

# Subestaciones de distribución (subtipo 2) sin código de estructura o voltajes
Enterprise_SUB04 = '''SUBTIPO = 2 AND (CODIGOESTRUCTURA IS NULL OR VPRIMARIO IS NULL OR VSECUNDARIO IS NULL)'''

# Subestaciones sin dirección
Enterprise_SUB05 = '''DIRECCION IS NULL'''

# Subestaciones sin nombre de la línea que energiza (TEXTOETIQUETA)
Enterprise_SUB06 = '''TEXTOETIQUETA IS NULL'''


# ==============================================================================
# QUERIES PARA CAPA "PUESTO TRANSFORMADOR DE POTENCIA"
# ==============================================================================

# Puestos de trafo de potencia sin relación a unidad en la tabla UnidadTransfPotencia
Enterprise_TP01 = '''(GLOBALID NOT IN (select u.PUESTOTRANSFPOTGLOBALID FROM sigelec.UNIDADTRANSFPOTENCIA u 
                WHERE u.PUESTOTRANSFPOTGLOBALID IS NOT NULL))'''

# Puestos de trafo de potencia con propiedad diferente de 'COD_EMPRESA' o 'PARTICULAR'
Enterprise_TP02 = "CODIGOEMPRESA NOT IN ('COD_EMPRESA','PARTICULAR') OR CODIGOEMPRESA IS NULL"

# Puestos de trafo de potencia con código de empresa incorrecto
Enterprise_TP03 = Enterprise_CodigoEmpresa

# Puestos de trafo de potencia sin GLOBALID de subestación
Enterprise_TP04 = "SUBESTACIONGLOBALID IS NULL"

# Puestos de trafo de potencia sin Provincia, Cantón o Parroquia
Enterprise_TP05 = Enterprise_ProvCantParr

# Puestos de trafo de potencia sin consistencia jerárquica
Enterprise_TP06 = Enterprise_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD TRANSFORMADOR DE POTENCIA"
# ==============================================================================

# Unidades de trafo de potencia con código de empresa incorrecto
Enterprise_UTP00 = Enterprise_CodigoEmpresa

# Unidades con potencia nominal mayor que la forzada, o con formato inválido
# (contiene 'kva', 'K', 'k', espacios, 'mva', 'M')
Enterprise_UTP01 = '''(POTENCIANOMINAL > POTENCIAFORZADA) AND POTENCIANOMINAL is not null OR POTENCIANOMINAL LIKE ('%kva%') 
                OR POTENCIANOMINAL LIKE ('%K%') OR POTENCIANOMINAL LIKE ('%k%') OR POTENCIANOMINAL LIKE ('% %') 
                OR POTENCIANOMINAL LIKE ('%mva%') OR POTENCIANOMINAL LIKE ('%M%')'''

# Unidades sin relación al puesto de trafo de potencia
Enterprise_UTP02 = '''(PUESTOTRANSFPOTGLOBALID NOT IN (select pt.GLOBALID FROM sigelec.PuestoTransfPotencia pt 
                WHERE pt.GLOBALID IS NOT NULL))'''

# Unidades sin Provincia, Cantón o Parroquia
Enterprise_UTP03 =Enterprise_ProvCantParr

# Unidades sin consistencia jerárquica
Enterprise_UTP04 = Enterprise_ConsistenciaProvCantParr


# ==============================================================================
# QUERIES PARA CAPA "TENSOR"
# ==============================================================================

# Tensores sin código de estructura o con código que no empieza con 'TA'
Enterprise_TE01 = "CODIGOESTRUCTURA IS NULL or CODIGOESTRUCTURA not like ('TA%')"

# Tensores con código de empresa incorrecto
Enterprise_TE02 = Enterprise_CodigoEmpresa

# Tensores sin Provincia, Cantón o Parroquia
Enterprise_TE03 = Enterprise_ProvCantParr

# Tensores sin consistencia jerárquica
Enterprise_TE04 = Enterprise_ConsistenciaProvCantParr

# Tensores sin poste asociado (ESTRUCTURASOPORTEGLOBALID nulo)
Enterprise_TE05 = '''ESTRUCTURASOPORTEGLOBALID IS NULL'''

# ==============================================================================
# QUERIES PARA CAPA "PUNTO VETADO"
# ==============================================================================

# Puntos vetados sin código único o con código de longitud diferente a 10 caracteres
Enterprise_VET01 = "CODIGOUNICO IS NULL or length(CODIGOUNICO)<>10"

# Puntos vetados con código de empresa incorrecto
Enterprise_VET02 = Enterprise_CodigoEmpresa

# ==============================================================================
# QUERIES PARA TABLA "INSTITUCIÓN EN POSTE"
# ==============================================================================

# Institución en poste con código de empresa incorrecto
Enterprise_INS01 = Enterprise_CodigoEmpresa

# Institución con código nulo o fuera del rango válido (1-50)
Enterprise_INS02 = "INSTITUCION IS NULL OR INSTITUCION NOT BETWEEN 1 AND 50"

# Institución sin relación a un poste existente en EstructuraSoporte
Enterprise_INS03 = "(ESTRUCTURASOPORTEGLOBALID NOT IN (select pt.GLOBALID FROM sigelec.EstructuraSoporte pt WHERE pt.GLOBALID IS NOT NULL)) "

# Institución sin GLOBALID de poste seleccionado
Enterprise_INS04 = "estructurasoporteglobalid is null"

# ==============================================================================
# QUERIES PARA CAPA "PROTECCIÓN BT"
# ==============================================================================

# Protección BT con código de empresa incorrecto
Enterprise_PBT01 = Enterprise_CodigoEmpresa

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD PROTECCIÓN DINÁMICA"
# ==============================================================================

# Unidad de protección dinámica con código de empresa incorrecto
Enterprise_UPD01 = Enterprise_CodigoEmpresa

# Unidad sin Provincia, Cantón o Parroquia
Enterprise_UPD02 = Enterprise_ProvCantParr

# Unidad sin consistencia jerárquica
Enterprise_UPD03 = Enterprise_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "ESTRUCTURAS SUBTERRÁNEAS"
# ==============================================================================

# Estructuras subterráneas con código de empresa incorrecto
Enterprise_ES01 = Enterprise_CodigoEmpresa

# Estructuras subterráneas donde MIGUID no coincide con GLOBALID o es nulo
Enterprise_ES02 = '''GLOBALID <> MIGUID OR MIGUID IS NULL'''

# Estructuras subterráneas sin Provincia, Cantón o Parroquia
Enterprise_ES03 = Enterprise_ProvCantParr

# Estructuras subterráneas sin consistencia jerárquica
Enterprise_ES04 = Enterprise_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "PUNTO APERTURA"
# ==============================================================================

# Punto apertura con código de empresa incorrecto
Enterprise_PA01 = Enterprise_CodigoEmpresa

# ==============================================================================
# QUERIES PARA CAPA "EQUIPOS DE TELECOMUNICACIONES"
# ==============================================================================

# Equipos de telecomunicaciones con código de empresa incorrecto
Enterprise_ET01 = Enterprise_CodigoEmpresa

# Equipos sin Provincia, Cantón o Parroquia
Enterprise_ET02 = Enterprise_ProvCantParr

# Equipos sin consistencia jerárquica
Enterprise_ET03 = Enterprise_ConsistenciaProvCantParr

# Equipos sin operadora, fecha de ingreso o contrato
Enterprise_ET04 = '''OPERADORA is null or FECHAINGRESO is null or CONTRATO is null'''

# Equipos sin detalle de equipo relacionado en la tabla DetalleEquipo
Enterprise_ET05 = '''GLOBALID not in (
                select UE.EQUIPOGLOBALID   
                FROM SIGELEC.DETALLEEQUIPO UE 
                WHERE UE.EQUIPOGLOBALID IS NOT NULL)'''

# ==============================================================================
# QUERIES PARA CAPA "TRAMO OPERADORA AÉREO"
# ==============================================================================

# Tramo operadora aéreo con código de empresa incorrecto
Enterprise_TO01 = Enterprise_CodigoEmpresa

# Tramo sin Provincia, Cantón o Parroquia
Enterprise_TO02 = Enterprise_ProvCantParr

# Tramo sin consistencia jerárquica
Enterprise_TO03 = Enterprise_ConsistenciaProvCantParr

# Tramo sin operadora, fecha de ingreso o contrato
Enterprise_TO04 = '''OPERADORA is null or FECHAINGRESO is null or CONTRATO is null'''

# Tramo sin detalle de tramo relacionado
Enterprise_TO05 = '''GLOBALID not in (
                select UE.TRAMOAGLOBALID   
                FROM SIGELEC.DetalleTramoOperadoraAereo UE 
                WHERE UE.TRAMOAGLOBALID IS NOT NULL)'''

# ==============================================================================
# QUERIES PARA TABLA "DETALLE EQUIPO"
# ==============================================================================

# Detalle equipo con código de empresa incorrecto
Enterprise_DE01 = Enterprise_CodigoEmpresa

# Detalle equipo sin Provincia, Cantón o Parroquia
Enterprise_DE02 = Enterprise_ProvCantParr

# Detalle equipo sin consistencia jerárquica
Enterprise_DE03 = Enterprise_ConsistenciaProvCantParr

# Detalle equipo sin operadora, fecha de ingreso, subtipo, tipo equipo o cantidad
Enterprise_DE04 = '''OPERADORA is null or FECHAINGRESO is null 
                or SUBTIPO IS NULL OR TIPOEQUIPO IS NULL 
                OR CANTIDADEQUIPO is null'''

# Detalle equipo sin equipo relacionado o con GLOBALID que no existe en tabla EQUIPO
Enterprise_DE05 = '''EQUIPOGLOBALID is null 
                or (EQUIPOGLOBALID NOT IN (
                select EQ.GLOBALID FROM SIGELEC.EQUIPO EQ 
                WHERE EQ.GLOBALID IS NOT NULL))'''

# ==============================================================================
# QUERIES PARA TABLA "DETALLE TRAMO"
# ==============================================================================

# Detalle tramo con código de empresa incorrecto
Enterprise_DT01 = Enterprise_CodigoEmpresa

# Detalle tramo sin Provincia, Cantón o Parroquia
Enterprise_DT02 = Enterprise_ProvCantParr

# Detalle tramo sin consistencia jerárquica
Enterprise_DT03 = Enterprise_ConsistenciaProvCantParr

# Detalle tramo sin operadora, fecha de ingreso, tipo conductor, cantidad o hilos de fibra
Enterprise_DT04 = '''OPERADORA is null or FECHAINGRESO is null 
                or TIPOCONDUCTOR IS NULL OR CANTIDAD IS NULL 
                OR CANTIDADHILOSFIBRA is null'''

# Detalle tramo sin tramo aéreo relacionado o con GLOBALID que no existe
Enterprise_DT05 = '''TRAMOAGLOBALID is null or (TRAMOAGLOBALID NOT IN (
                select EQ.GLOBALID FROM SIGELEC.TramoOperadoraAereo EQ 
                WHERE EQ.GLOBALID IS NOT NULL))'''

# ==============================================================================
# DICCIONARIOS DE VALIDACIÓN POR CAPA (Layers)
# ==============================================================================
# Cada diccionario agrupa las queries por capa/tabla del GIS.
# La clave es un identificador descriptivo y el valor es la query SQL.
# El motor de reportes (generarReporte20.py) itera sobre estos diccionarios
# para ejecutar cada validación y contabilizar errores.
# ==============================================================================

# --- Punto de Carga ---
QuerysPuntoCarga =      {'Enterprise_10_PC_Punto de Carga con Mas 100 Conexion Consumidor': Enterprise_PC10,
                        'Enterprise_11_PC_Punto de Carga con Mas De 1 Transformador Asociado': Enterprise_PC11,
                        'Enterprise_12_PC_Punto de Carga con Alimentador y Enabled en No': Enterprise_PC12,
                        'Enterprise_13_PC_Punto de Carga con Alimentador diferente a su transformador': Enterprise_PC13,
                        'Enterprise_14_PC_Punto de Carga Totalizador Con Mas De 1 Conexion': Enterprise_PC14,
                        'Enterprise_16_PC_Medidor PC Totalizador Pero AC Tarifa Incorrecta': Enterprise_PC16,
                        'Enterprise_18_PC_Punto de Carga Coordenadas Desactualizadas': Enterprise_PC18,
                        'Enterprise_19_PC_Provincia Canton Parroquia Diferentes Entre Puesto Y Unidad': Enterprise_PC19,
                        'Enterprise_20_PC_Subtipo Alto Voltaje Y No Lleno La S_E A La Que Se Conecta': Enterprise_PC20,
                        'Enterprise_21_PC_Punto de carga sin Globalid de Acometida': Enterprise_PC21}

# --- Luminaria ---
QuerysLuminaria =       {'Enterprise_07_LUM_Fuente Energia': Enterprise_LUM07,
                        'Enterprise_08_LUM_Sin Potencia': Enterprise_LUM08,
                        'Enterprise_09_LUM_Clasificacion AP Bajo Medicion Propiedad Fuente Energia': Enterprise_LUM09,
                        'Enterprise_12_LUM_Codigo Estructura De 120V Pero Con Secuencia De Fase De 240V': Enterprise_LUM12,
                        'Enterprise_13_LUM_Con Alimentador y Enabled En No': Enterprise_LUM13,
                        'Enterprise_14_LUM_Mal La Relacion Fase Con Secuencia De Fase o Circuitos': Enterprise_LUM14,
                        'Enterprise_15_LUM_Circuito Mal Ingresado En Trafo No Monofasico': Enterprise_LUM15,
                        'Enterprise_16_LUM_Circuito Mal Ingresado En Trafo Monofasico': Enterprise_LUM16,
                        'Enterprise_17_LUM_Potencia Ingresada Diferente A Potencia De Catalogo Estructura': Enterprise_LUM17,
                        'Enterprise_18_LUM_Luminaria_con Alimentador Diferente A Su Transformador': Enterprise_LUM18,
                        'Enterprise_19_LUM_Codigo De Estructura No Corresponde Al Subtipo': Enterprise_LUM19,
                        'Enterprise_21_LUM_Potencia Menor a 60W y Mayor a 600W de Propiedad de la Empresa': Enterprise_LUM21,
                        'Enterprise_22_LUM_Alimentador Particular y Trafo Propiedad de la Empresa': Enterprise_LUM22,
                        'Enterprise_23_LUM_GLOBALID diferente a MIGUID ': Enterprise_LUM23,
                        'Enterprise_24_LUM_Con alimentador sin poste relacionado': Enterprise_LUM24,
                        'Enterprise_25_LUM_Doble nivel incorrecto': Enterprise_LUM25}

# --- Transformador de Distribución ---
QuerysPuestoTransformador =     {'Enterprise_21_PTD_Circuit Source Repetido': Enterprise_PTD21,
                                'Enterprise_22_PTD_Transformadores Con Mas De 100 luminarias': Enterprise_PTD22,
                                'Enterprise_23_PTD_Transformadores Con Mas De 100 Punto de Carga ': Enterprise_PTD23,
                                'Enterprise_24_PTD_Con BTA Relacionados Pero Diferentes Alimentadores': Enterprise_PTD24,
                                'Enterprise_25_PTD_Con BTS Relacionados Pero Diferentes Alimentadores': Enterprise_PTD25,
                                'Enterprise_27_PTD_Tipo Red': Enterprise_PTD27,
                                'Enterprise_28_PTD_Tipo Trafo': Enterprise_PTD28,
                                'Enterprise_30_PTD_Transformador Sobrecarga > 200': Enterprise_PTD30,
                                'Enterprise_31_PTD_Codigo De Estructura Del Puesto Diferente De La Unidad': Enterprise_PTD31,
                                'Enterprise_32_PTD_Potencia Ingresada Diferente a Potencia De Catalogo Estructura': Enterprise_PTD32,
                                'Enterprise_33_PTD_Transformadores De Tipo Alumbrado Pero Con Mas De 2 Clientes': Enterprise_PTD33,
                                'Enterprise_34_PTD_Tipo De Transformador Del Puesto Diferente De La Unidad': Enterprise_PTD34,
                                'Enterprise_35_PTD_Voltaje Secundario Del Puesto Diferente De La Unidad': Enterprise_PTD35,
                                'Enterprise_36_PTD_Codigo De Estructura Inconsistente Con Subtipo': Enterprise_PTD36,
                                'Enterprise_37_PTD_Transformadores Con Mas De 1 Totalizador': Enterprise_PTD37,
                                'Enterprise_39_PTD_Provincia Canton Parroquia Diferentes Entre Puesto Y Unidad': Enterprise_PTD39,
                                'Enterprise_40_PTD_Alimentador Particular Y Trafo Propiedad de la Empresa': Enterprise_PTD40,
                                'Enterprise_41_PTD_GLOBALID diferente a MIGUID': Enterprise_PTD41,
                                'Enterprise_42_PTD_Sin poste asociado': Enterprise_PTD42,
                                'Enterprise_43_PTD_Con luminarias medidas sin punto carga tipo alumbrado': Enterprise_PTD43,
                                'Enterprise_44_PTD_Sin cantidad de clientes o luminarias': Enterprise_PTD44}

# --- Regulador de Tensión ---
QuerysReguladorTension =        {'Enterprise_08_PRT_Control de la Empresa': Enterprise_PRT08,
                                'Enterprise_09_PRT_Codigo Estructura': Enterprise_PRT09}

# --- Seccionador Cuchilla ---
QuerysSeccionadorCuchilla =     {'Enterprise_08_PSC_Tipo Uso Y Codigo Estructura': Enterprise_PSC08,
                                'Enterprise_11_PSC_Seccionador Cuchilla Con Alimentador Y Enabled En No': Enterprise_PSC11,
                                'Enterprise_13_PSC_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_PSC13,
                                'Enterprise_14_PSC_Provincia Canton Parroquia': Enterprise_PSC14,
                                'Enterprise_15_PSC_Codigo Estructura Inconsistente Con Fases': Enterprise_PSC15}

# --- Protección Dinámica ---
QuerysProteccionDinamico =      {'Enterprise_09_PPD_Control': Enterprise_PPD09,
                                'Enterprise_10_PPD_Subsource Incorrecto': Enterprise_PPD10,
                                'Enterprise_11_PPD_Tipo Uso': Enterprise_PPD11}

# --- Seccionador Fusible ---
QuerysSeccionadorFusible =      {'Enterprise_09_PSF_Corriente Nominal': Enterprise_PSF09,
                                'Enterprise_10_PSF_Codigo Estructura': Enterprise_PSF10,
                                'Enterprise_11_PSF_Seccionador Con Alimentador Y Enabled En No': Enterprise_PSF11,
                                'Enterprise_12_PSF_Tirafusible Mal Ingresado': Enterprise_PSF12,
                                'Enterprise_13_PSF_Monofasico Cantidad De Unidades Incorrectas': Enterprise_PSF13,
                                'Enterprise_14_PSF_Bifasico Cantidad De Unidades Incorrectas': Enterprise_PSF14,
                                'Enterprise_15_PSF_Trifasico Cantidad De Unidades Incorrectas': Enterprise_PSF15,
                                'Enterprise_16_PSF_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_PSF16,
                                'Enterprise_17_PSF_Provincia Canton Parroquia': Enterprise_PSF17,
                                'Enterprise_18_PFC_Codigo Estructura Inconsistente Con Fases': Enterprise_PSF18}

# --- Semáforo ---
QuerysSemaforo =        {'Enterprise_07_SEM_Incorrecto Horas Func1 y Horas Func2 Dias FuncMes': Enterprise_SEM07,
                        'Enterprise_08_SEM_Semaforo Con Alimentador y Enabled En No': Enterprise_SEM08,
                        'Enterprise_09_SEM_Semaforo Mal La Relacion Fase Con Secuencia De Fase o Circuitos': Enterprise_SEM09,
                        'Enterprise_10_SEM_Semaforo Circuito Mal Ingresado En Trafo No Monofasico': Enterprise_SEM10,
                        'Enterprise_11_SEM_Semaforo Circuito Mal Ingresado En Trafo Monofasico': Enterprise_SEM11,
                        'Enterprise_12_SEM_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_SEM12,
                        'Enterprise_13_SEM_Provincia Canton Parroquia': Enterprise_SEM13}

# --- Capacitor (vacío - sin validaciones de la Empresa adicionales) ---
QuerysCapacitor =   {

}

# --- Protección BT ---
QuerysProteccionBT = {'Enterprise_01_PBT_Codigo Empresa': Enterprise_PBT01}

# --- Transformador de Potencia ---
QuerysTransformadorPotencia =   {'Enterprise_01_PTP_Puesto Sin Relacion Unidad Trafo Potencia': Enterprise_TP01,
                                'Enterprise_02_PTP_Propiedad': Enterprise_TP02,
                                'Enterprise_03_PTP_Codigo Empresa': Enterprise_TP03,
                                'Enterprise_04_PTP_Sin GlobalID Subestacion': Enterprise_TP04,
                                'Enterprise_05_PTP_Provincia Canton Parroquia': Enterprise_TP05,
                                'Enterprise_06_PTP_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_TP06}

# --- Punto Vetado ---
QuerysPuntoVetado =     {'Enterprise_01_VET_Vetado Sin Codigo Unico O Incorrecto': Enterprise_VET01,
                        'Enterprise_02_VET_Codigo Empresa': Enterprise_VET02}

# --- Punto Apertura (comentado por ahora) ---
QuerysPuntoApertura =   {# 'Enterprise_01_PA_Codigo Empresa': Enterprise_PA01
                        }

# --- Barra ---
QuerysBarra = {'Enterprise_BAR_01_Codigo Empresa': Enterprise_BAR01}

# --- Tramos MT ---
QuerysMT =      {'Enterprise_07_MT_Bajantes Longitud Incorrecta 20cm y 3 Metros': Enterprise_MT07,
                'Enterprise_08_MT_Con Alimentador Pero NO Admite Traces': Enterprise_MT08,
                'Enterprise_09_MT_Con Alimentador y Enabled En No': Enterprise_MT09,
                'Enterprise_10_MT_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_MT10,
                'Enterprise_11_MT_Provincia Canton Parroquia': Enterprise_MT11}

# --- Tramos BT ---
QuerysBT =      {'Enterprise_01_BT_Fase Conexion Alimentador INFO': Enterprise_BT01,
                'Enterprise_02_BT_Acometidas Longitud Incorrecta 500 Metros': Enterprise_BT02,
                'Enterprise_03_BT_Codigo Empresa': Enterprise_BT03,
                'Enterprise_04_BT_AlimentadorID Desconectados': Enterprise_BT04,
                'Enterprise_05_BT_Calibre Fase o Neutro': Enterprise_BT05,
                'Enterprise_06_BT_Voltaje': Enterprise_BT06,
                'Enterprise_07_BT_Con Alimentador y Enabled En No': Enterprise_BT07,
                'Enterprise_08_BT_Voltaje 240V_Configuracion Conductores Circuito': Enterprise_BT08,
                'Enterprise_09_BT_Voltaje 208V_220V Configuracion Conductor Circuito': Enterprise_BT09,
                'Enterprise_10_BT_Voltaje 120V_127V Configuracion De Conductores Circuito': Enterprise_BT10,
                'Enterprise_11_BT_Voltaje 208V Banco 3 transformadores BT': Enterprise_BT11,
                'Enterprise_12_BT_Voltaje 120_240V': Enterprise_BT12,
                'Enterprise_13_BT_Voltaje 127_220V': Enterprise_BT13,
                'Enterprise_14_BT_Configuracion Conductores 2F2C 2F3C 3F3C 3F4C': Enterprise_BT14,
                'Enterprise_15_BT_Circuito Conductores Banco 2 Transformadores': Enterprise_BT15,
                'Enterprise_16_BT_Circuito Conductores Monofasicos': Enterprise_BT16,
                'Enterprise_17_BT_Circuito Conductores Bifasicos': Enterprise_BT17,
                'Enterprise_18_BT_Conductor Fase': Enterprise_BT18,
                'Enterprise_19_BT_Aerea Provincia Canton Parroquia': Enterprise_BT19,
                'Enterprise_20_BT_Circuitos': Enterprise_BT20,
                'Enterprise_21_BT_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_BT21,
                'Enterprise_22_BT_Mal La Relacion Fase Con Secuencia De Fase o Circuitos': Enterprise_BT22}

# --- Tramos Subtransmisión ---
QuerysTramosST =        {'Enterprise_01_ST_Codigo Empresa': Enterprise_ST01,
                        'Enterprise_02_ST_Calibre Fase o Neutro': Enterprise_ST02,
                        'Enterprise_03_ST_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_ST03,
                        'Enterprise_04_ST_AlimentadorID': Enterprise_ST04,
                        'Enterprise_05_ST_Sin Nombre De linea': Enterprise_ST05}

# --- Subestación ---
QuerysSubestacion =     {'Enterprise_01_SUB_Subtipo incorrecto o Sin Nombre': Enterprise_SUB01,
                        'Enterprise_02_SUB_Codigo De Empresa': Enterprise_SUB02,
                        'Enterprise_03_SUB_Subestacion Sin Trafo Potencia': Enterprise_SUB03,
                        'Enterprise_04_SUB_Subestacion sin codigo estructura o voltajes': Enterprise_SUB04,
                        'Enterprise_05_SUB_Subestacion sin direccion': Enterprise_SUB05,
                        'Enterprise_06_SUB_Subestacion sin LTS que energiza': Enterprise_SUB06}

# --- Poste ---
QuerysPoste =   {'Enterprise_01_POS_Numero Poste Repetido': Enterprise_POS01,
                'Enterprise_02_POS_Codigo Estructura': Enterprise_POS02,
                'Enterprise_03_POS_Tipo Uso Postes': Enterprise_POS03,
                'Enterprise_04_POS_Placa En Null': Enterprise_POS04,
                'Enterprise_05_POS_Codigo Empresa': Enterprise_POS05,
                'Enterprise_06_POS_Provincia Canton Parroquia': Enterprise_POS06,
                'Enterprise_07_POS_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_POS07,
                'Enterprise_08_POS_Codigo De Estructura No Corresponde Al Subtipo': Enterprise_POS08,
                'Enterprise_10_POS_Sin Estructura En Poste': Enterprise_POS10,
                'Enterprise_11_POS_Propiedad': Enterprise_POS11,
                'Enterprise_12_POS_Global Diferente A MIGUID': Enterprise_POS12,
                'Enterprise_13_POS_Coordenada De Poste Desactualizada': Enterprise_POS13}

# --- Estructura Subterránea ---
QuerysEstructuraSubterranea =   {'Enterprise_01_ES_Codigo Empresa': Enterprise_ES01,
                                'Enterprise_02_ES_GlobalID Diferente A MIGUID':Enterprise_ES02,
                                'Enterprise_03_ES_Provincia Canton Parroquia': Enterprise_ES03,
                                'Enterprise_04_ES_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_ES04}

# --- Tensor ---
QuerysTensor =  {'Enterprise_01_TE_Codigo Estructura': Enterprise_TE01,
                'Enterprise_02_TE_Codigo Empresa': Enterprise_TE02,
                'Enterprise_03_TE_Provincia Canton Parroquia': Enterprise_TE03,
                'Enterprise_04_TE_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_TE04,
                'Enterprise_05_TE_Sin poste asociado': Enterprise_TE05}

# --- Equipos de Telecomunicación ---
QuerysEquipoTelcom = {
                        'Enterprise_01_ET_Codigo Empresa' : Enterprise_ET01,
                        'Enterprise_02_ET_Provincia Canton Parroquia': Enterprise_ET02,
                        'Enterprise_03_ET_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_ET03,
                        'Enterprise_04_ET_Sin cableoperadora o contrato o fecha ingreso' : Enterprise_ET04,
                        'Enterprise_05_ET_Sin detalle equipo relacionado' : Enterprise_ET05}

# --- Tramos Telecomunicaciones ---
QuerysTramoTelcom = {
                        'Enterprise_01_TO_Codigo Empresa' : Enterprise_TO01,
                        'Enterprise_02_TO_Provincia Canton Parroquia': Enterprise_TO02,
                        'Enterprise_03_TO_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_TO03,
                        'Enterprise_04_TO_Sin cableoperadora o contrato o fecha ingreso' : Enterprise_TO04,
                        'Enterprise_05_TO_Sin detalle tramo relacionado' : Enterprise_TO05}

# ==============================================================================
# DICCIONARIOS DE VALIDACIÓN POR TABLA
# ==============================================================================

# --- Atributos Consumidor (vacío - sin validaciones de la Empresa) ---
QuerysAtributosConsumidor =  {

}

# --- Conexión Consumidor ---
QuerysConexionConsumidor =      {'Enterprise_08_CC_Codigo Unico Pero Lleno El Campo Novedad': Enterprise_CC08,
                                'Enterprise_09_CC_Sin GlobalID Del Punto de Carga ': Enterprise_CC09,
                                'Enterprise_10_CC_Codigo Unico No Acorde A Codigo Empresa': Enterprise_CC10}

# --- Unidad Transformador ---
QuerysUTransformador =  {'Enterprise_11_UT_Sticker = Null': Enterprise_UTD11,
                        'Enterprise_12_UT_Propiedad de la Empresa': Enterprise_UTD12,
                        'Enterprise_13_UT_Tipo Trafo': Enterprise_UTD13,
                        'Enterprise_14_UT_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_UTD14,
                        'Enterprise_15_UT_Codigo Estructura Inconsistente': Enterprise_UTD15,
                        'Enterprise_16_UT_Alimentador Particular y Trafo Propiedad de la Empresa': Enterprise_UTD16,
                        'Enterprise_17_UT_Propiedad Diferente Entre Puesto y Unidad': Enterprise_UTD17,
                        'Enterprise_18_UT_Potencia unidad transformador diferente de catalogo': Enterprise_UTD18}

# --- Unidad Capacitor ---
QuerysUnidadCapacitor = {'Enterprise_06_UC_Codigo Estructura': Enterprise_UCAP06}

# --- Circuito Fuente ---
QuerysCircuitoFuente =  {'Enterprise_00_CF_Codigo Empresa': Enterprise_CF00,
                        'Enterprise_01_CF_Consistencia Alimentador Subestacion': Enterprise_CF01,
                        'Enterprise_02_CF_Zona Influencia': Enterprise_CF02,
                        'Enterprise_XX_CF_Troncal MTA Con Mas De 4 Conductores': Enterprise_CFXX}

# --- Unidad Regulador ---
QuerysUnidadRegulador = {'Enterprise_06_UREG_Codigo ADMS Repetido': Enterprise_URT06,
                        'Enterprise_07_UREG_Codigo Estructura': Enterprise_URT07}

# --- Estructura en Poste ---
QuerysEstructuraPoste = {'Enterprise_01_ESP_Estructura En Poste Sin Poste': Enterprise_ESP01,
                        'Enterprise_02_ESP_Estructura En Poste Codigo Empresa': Enterprise_ESP02,
                        'Enterprise_03_ESP_Estructura En Poste Codigo Estructura': Enterprise_ESP03,
                        'Enterprise_04_ESP_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_ESP04,
                        'Enterprise_05_ESP_Provincia Canton Parroquia': Enterprise_ESP05}

# --- Unidad Fusible ---
QuerysUnidadFusible =   {'Enterprise_01_UF_Fase Conexion': Enterprise_UF01,
                        'Enterprise_02_UF_Tirafusible': Enterprise_UF02}

# --- Institución en Poste ---
QuerysInstitucionPoste =        {'Enterprise_01_INS_Codigo Empresa': Enterprise_INS01,
                                'Enterprise_02_INS_Institucion En Null O Ingresando Como Texto': Enterprise_INS02,
                                'Enterprise_03_INS_Institucion Sin Poste Relacionado': Enterprise_INS03,
                                'Enterprise_04_INS_Institucion Sin GlobalID Seleccionado': Enterprise_INS04}

# --- Unidad Protección Dinámica ---
QuerysUnidadProteccionDinamico =        {'Enterprise_01_UPD_Codigo Empresa': Enterprise_UPD01,
                                        'Enterprise_02_UPD_Provincia Canton Parroquia': Enterprise_UPD02,
                                        'Enterprise_03_UPD_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_UPD03}

# --- Unidad Transformador de Potencia ---
QuerysUnidadTransformadorPotencia =     {'Enterprise_00_UTP_Codigo Empresa': Enterprise_UTP00,
                                        'Enterprise_01_UTP_Potencia Forzada Mayor Que Nominal': Enterprise_UTP01,
                                        'Enterprise_02_UTP_Unidad Sin Relacion Puesto TransfPotencia': Enterprise_UTP02,
                                        'Enterprise_03_Provincia Canton Parroquia': Enterprise_UTP03,
                                        'Enterprise_04_UTP_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_UTP04}

# --- Detalle Equipo ---
QueryDetalleEquipo = {
                        'Enterprise_01_DE_Codigo Empresa' : Enterprise_DE01,
                        'Enterprise_02_DE_Provincia Canton Parroquia' : Enterprise_DE02,
                        'Enterprise_03_DE_No existe Consistencia Entre Provincia Canton Parroquia': Enterprise_DE03,
                        'Enterprise_04_DE_Sin cableoperadora o contrato o fecha ingreso' : Enterprise_DE04,
                        'Enterprise_05_DE_Sin equipo relacionado': Enterprise_DE05}

# --- Detalle Tramo ---
QueryDetalleTramo = {
                        'Enterprise_01_DT_Codigo Empresa' : Enterprise_DT01,
                        'Enterprise_02_DT_Provincia Canton Parroquia' : Enterprise_DT02,
                        'Enterprise_03_DT_No existe Consistencia Entre Provincia Canton Parroquia' : Enterprise_DT03,
                        'Enterprise_04_DT_Sin cableoperadora o contrato o fecha ingreso' : Enterprise_DT04,
                        'Enterprise_05_DT_Sin equipo relacionado' : Enterprise_DT05}

# ==============================================================================
# DICCIONARIO SISTOT (Órdenes de trabajo)
# ==============================================================================
# Valida que los campos de orden de trabajo no contengan letras
# en varias capas que gestionan SISTOT.
# ==============================================================================
QuerysSISTOT = {'SISTOT_LUM_20_Orden_de_Trabajo_Incorrecto': Enterprise_LUM20,
                'SISTOT_PC_17_Orden_de_Trabajo_Incorrecto': Enterprise_PC17,
                'SISTOT_POS_09_Orden_de_Trabajo_Incorrecto': Enterprise_POS09,
                'SISTOT_PPD_12_Orden_de_Trabajo_Incorrecto': Enterprise_PPD12,
                'SISTOT_PRT_10_Orden_de_Trabajo_Incorrecto': Enterprise_PRT10,
                'SISTOT_PSC_12_Orden_de_Trabajo_Incorrecto': Enterprise_PSC12,
                'SISTOT_PTD_38_Orden_de_Trabajo_Incorrecto': Enterprise_PTD38}