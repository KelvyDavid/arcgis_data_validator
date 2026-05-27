# ==============================================================================
# CIS_Querys.py
# ==============================================================================
# Módulo de queries de validación para el sistema CIS (Customer Information System).
# Contiene consultas SQL (cláusulas WHERE) que validan la consistencia de datos
# en la red de distribución eléctrica desde la perspectiva del sistema comercial.
#
# Las validaciones abarcan:
#   - Tramos de Baja Tensión (BT): acometidas aéreas y subterráneas
#   - Puntos de Carga: conexión y alimentación
#   - Conexiones de Consumidor: circuitos, relaciones y geografía
#   - Luminarias: funcionamiento, estructura y fuente de energía
#   - Protección Dinámica y Subestaciones
#   - Transformadores de Distribución: voltaje, subtipo y estructura
#   - Unidades de Transformador y Atributos del Consumidor
#
# Cada constante almacena una cláusula WHERE que, al ejecutarse con arcpy,
# selecciona los registros que NO cumplen con la regla de negocio (errores).
# ==============================================================================

# ==========================================
# Queries comunes reutilizables
# ==========================================

# Valida que el código de empresa sea 'COD_EMPRESA' (no nulo ni diferente)
Enterprise_CodigoEmpresa = "CODIGOEMPRESA IS NULL OR CODIGOEMPRESA NOT IN ('COD_EMPRESA')"

# Valida que los campos de ubicación geográfica (Provincia, Cantón, Parroquia) no sean nulos ni vacíos
CIS_ProvCantParr = '''(PROVINCIA is null or CANTON is null or PARROQUIA is null or 
                        PROVINCIA =  '' or CANTON = '' or PARROQUIA = '')'''

# Valida la consistencia jerárquica de los códigos geográficos:
# - Los 2 primeros dígitos de CANTON deben coincidir con PROVINCIA
# - Los 4 primeros dígitos de PARROQUIA deben coincidir con CANTON
CIS_ConsistenciaProvCantParr = "((PROVINCIA <> substr(CANTON, 0,2)) or (CANTON <> substr(PARROQUIA, 0,4)))"

# ==============================================================================
# QUERIES PARA CAPA "TRAMOS BT" (Baja Tensión - Acometidas)
# ==============================================================================
# Las acometidas son subtipos 7, 8 y 9 dentro de la capa de tramos BT.
# Estas queries validan la consistencia entre voltaje, configuración de
# conductores, circuitos y el tipo de transformador al que están conectadas.
# ==============================================================================

# Acometidas bifásicas y trifásicas conectadas a transformadores monofásicos (subtipo 1F)
# Error: una acometida de subtipo 8 o 9 no debería estar asociada a un trafo monofásico (subtipo 1,2,3,4)
CIS_BT01 = '''(SUBTIPO IN (8,9) AND (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion PD WHERE (( PD.SUBTIPO  IN (1,2,3,4))))))'''

# Acometidas con voltaje 240V: valida que la configuración de conductores y circuitos
# sea compatible (configuraciones: 13, 14, 23, 24, 34; circuitos: AB, BC, AC, ABC, F12)
CIS_BT02 = '''SUBTIPO IN (7,8,9) and VOLTAJE in ('240') AND 
                (CONFIGURACIONCONDUCTORES not in ('13', '14','23','24', '34') or 
                CIRCUITOS  not in ( 'AB' , 'BC' , 'AC', 'ABC','F12'))'''

# Acometidas con voltaje 208V o 220V: valida configuración de conductores (23, 24, 34)
# y circuitos compatibles (AB, BC, AC, ABC)
CIS_BT03 = '''SUBTIPO IN (7,8,9) and VOLTAJE in ('208', '220') AND 
                (CONFIGURACIONCONDUCTORES not in ('23', '24', '34') or 
                CIRCUITOS not in ( 'AB' , 'BC' , 'AC', 'ABC'))'''

# Acometidas con voltaje 120V o 127V: valida configuración de conductores (12, 14)
# y circuitos compatibles (A, B, C, F1, F2) para líneas monofásicas
CIS_BT04 = '''SUBTIPO IN (7,8,9) and VOLTAJE in ('120', '127') AND 
                (CONFIGURACIONCONDUCTORES not in ('12', '14') or 
                CIRCUITOS not in ( 'A' , 'B' , 'C', 'F1', 'F2'))'''

# Acometidas con voltaje 208V: no deberían estar conectadas a trafos que NO sean
# banco 3F (subtipos 11,12 = banco trifásico que da 208V)
CIS_BT05 = '''(VOLTAJE  IN ('208') AND SUBTIPO IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select  PD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion PD WHERE (( PD.SUBTIPO  NOT IN (11,12))))))'''

# Acometidas con voltaje 120V o 240V: no deberían conectarse a trafos que NO sean
# monofásicos (1,2,3,4), bancos 2F (9,10) o bancos 3F (11,12)
CIS_BT06 = '''(VOLTAJE  IN ('120', '240') AND  SUBTIPO  IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select  PD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion PD WHERE (( PD.SUBTIPO NOT IN (1,2,3,4,9,10,11,12))))))'''

# Acometidas con voltaje 127V o 220V: no deberían conectarse a trafos que NO sean
# trifásicos (5,6,7,8) o bifásicos (13,14,15,16)
CIS_BT07 = '''(VOLTAJE  IN ('127', '220') AND SUBTIPO  IN (7,8,9)  AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion PD WHERE (( PD.SUBTIPO  NOT IN (5, 6, 7, 8, 13, 14, 15, 16))))))'''

# Acometidas con config. conductores bifásica/trifásica (22,23,33,34) conectadas
# a trafos monofásicos (subtipo 1,2,3,4) - incompatibilidad
CIS_BT08 = '''(CONFIGURACIONCONDUCTORES in ('22','23','33','34') AND SUBTIPO IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion PD WHERE (( PD.SUBTIPO   IN (1,2,3,4))))))'''

# Acometidas con config. conductores monofásica (13,14,11,22) conectadas a bancos de 2 trafos (9,10)
# cuya estructura NO es banco paralelo (no empieza con '1B' ni '1V')
CIS_BT09 = '''CONFIGURACIONCONDUCTORES in ('13','14', '11','22') AND  SUBTIPO IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE ((PD.SUBTIPO IN (9, 10) and PD.CODIGOESTRUCTURA in (select CE.CODIGOESTRUCTURA 
                FROM SIGELEC.CATALOGOESTRUCTURA CE where (CE.DESCRIPCIONCORTA not LIKE '1B%' AND 
                CE.DESCRIPCIONCORTA not LIKE '1V%'))))))'''

# Acometidas cuya configuración NO es (12,13,14) conectadas a bancos de 2 trafos (9,10)
# con estructura de banco paralelo (empieza con '1B' o '1V')
CIS_BT10 = '''CONFIGURACIONCONDUCTORES not in ('12','13','14') AND SUBTIPO IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE ((PD.SUBTIPO IN (9, 10) and PD.CODIGOESTRUCTURA in (select CE.CODIGOESTRUCTURA 
                FROM SIGELEC.CATALOGOESTRUCTURA CE where (CE.DESCRIPCIONCORTA LIKE '1B%' 
                or CE.DESCRIPCIONCORTA LIKE '1V%'))))))'''

# Acometidas con config. conductores (13,14) conectadas a trafos trifásicos o bifásicos
# (subtipos 5-8, 11-16) - la configuración no es compatible
CIS_BT11 = '''(CONFIGURACIONCONDUCTORES in ('13','14') AND SUBTIPO IN (7,8,9) AND 
                (PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO   IN (5, 6, 7, 8, 11, 12, 13, 14, 15, 16))))))'''

# Acometidas con circuitos F1, F2, F12 conectadas a bancos de 2 trafos (9,10)
# cuya estructura NO es banco paralelo (no '1B' ni '1V')
CIS_BT12 = '''(CIRCUITOS in ( 'F1' , 'F2' , 'F12') AND SUBTIPO IN (7,8,9)) AND (PARENTCIRCUITSOURCEGUID IN 
                (select  PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (PD.SUBTIPO IN (9,10) and PD.CODIGOESTRUCTURA in (select CE.CODIGOESTRUCTURA 
                FROM SIGELEC.CATALOGOESTRUCTURA CE where (CE.DESCRIPCIONCORTA  not LIKE '1B%' 
                and CE.DESCRIPCIONCORTA not LIKE '1V%')))))'''

# Acometidas con circuitos diferentes de F1, F2, F12 conectadas a bancos de 2 trafos (9,10)
# con estructura de banco paralelo ('1B' o '1V')
CIS_BT13 = '''(CIRCUITOS not in ( 'F1' , 'F2' , 'F12') AND SUBTIPO IN (7,8,9)) AND (PARENTCIRCUITSOURCEGUID IN 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (PD.SUBTIPO  IN (9,10) and PD.CODIGOESTRUCTURA in (select CE.CODIGOESTRUCTURA 
                FROM SIGELEC.CATALOGOESTRUCTURA CE where (CE.DESCRIPCIONCORTA LIKE '1B%' 
                or CE.DESCRIPCIONCORTA LIKE '1V%')))))'''

# Acometidas con circuitos F1, F2, F12 conectadas a trafos trifásicos o bifásicos
# (subtipos 5-16) - circuitos monofásicos en trafo no monofásico
CIS_BT14 = '''(CIRCUITOS in ( 'F1' , 'F2' , 'F12') AND SUBTIPO IN (7,8,9)) AND (PARENTCIRCUITSOURCEGUID IN 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE ( PD.SUBTIPO  IN (5, 6, 7, 8, 11, 12, 13, 14, 15, 16))))'''

# Acometidas con circuitos trifásicos/bifásicos (A,B,C,AB,BC,AC,ABC) conectadas
# a trafos monofásicos (subtipo 1,2,3,4) - circuitos multifásicos en trafo monofásico
CIS_BT15 = '''(CIRCUITOS in ( 'A' , 'B' , 'C', 'AB' , 'BC' , 'AC',  'ABC') AND SUBTIPO IN (7,8,9) AND 
                ((PARENTCIRCUITSOURCEGUID IN (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE (( PD.SUBTIPO  IN (1,2,3,4)))))))'''

# Acometidas con código de conductor de fase que no sigue el patrón 'COO____' (7 caracteres)
# o que es nulo/vacío
CIS_BT16 = '''SUBTIPO IN (7,8,9) AND ((CODIGOCONDUCTORFASE NOT LIKE '%COO____%') OR (CODIGOCONDUCTORFASE is null) or 
                (CODIGOCONDUCTORFASE = ''))'''

# Acometidas con configuración de conductores nula o que contiene 'F' (formato inválido)
CIS_BT17 = "SUBTIPO IN (7,8,9) AND ((CONFIGURACIONCONDUCTORES IS NULL) or (CONFIGURACIONCONDUCTORES like '%F%'))"

# Acometidas aéreas sin Provincia, Cantón o Parroquia completos
CIS_BT18 = "SUBTIPO IN (7,8,9) AND " + CIS_ProvCantParr

# Acometidas con circuitos nulos o escritos en minúsculas (deben ser mayúsculas)
CIS_BT19 = '''SUBTIPO IN (7,8,9) AND ((CIRCUITOS IS NULL) 
                OR (CIRCUITOS IN ('a','b','c','ab','ac','bc','abc','f1','f2','f12')))'''

# Acometidas sin consistencia entre Provincia, Cantón y Parroquia (jerarquía de códigos)
CIS_BT19_1 = "SUBTIPO IN (7,8,9) AND " + CIS_ConsistenciaProvCantParr

# Acometidas cuyo código de conductor de fase no está dentro del catálogo válido
# (COO0001 a COO0375 y algunos adicionales hasta COO0412)
CIS_BT19_2 = '''SUBTIPO IN (7,8,9) AND (CODIGOCONDUCTORFASE  NOT IN ('COO0001', 'COO0002', 'COO0003', 'COO0004', 
                'COO0005', 'COO0006', 'COO0007', 'COO0008', 'COO0009', 'COO0010', 'COO0011', 'COO0012', 'COO0013', 
                'COO0014', 'COO0015', 'COO0016', 'COO0017', 'COO0018', 'COO0019', 'COO0020', 'COO0021', 'COO0022', 
                'COO0023', 'COO0024', 'COO0025', 'COO0026', 'COO0027', 'COO0028', 'COO0029', 'COO0030', 'COO0031', 
                'COO0032', 'COO0033', 'COO0034', 'COO0035', 'COO0036', 'COO0037', 'COO0038', 'COO0039', 'COO0040', 
                'COO0041', 'COO0042', 'COO0043', 'COO0044', 'COO0045', 'COO0046', 'COO0047', 'COO0048', 'COO0049', 
                'COO0050', 'COO0051', 'COO0052', 'COO0053', 'COO0054', 'COO0055', 'COO0056', 'COO0057', 'COO0058', 
                'COO0059', 'COO0060', 'COO0061', 'COO0062', 'COO0063', 'COO0064', 'COO0065', 'COO0066', 'COO0067', 
                'COO0068', 'COO0069', 'COO0070', 'COO0071', 'COO0072', 'COO0073', 'COO0074', 'COO0075', 'COO0076', 
                'COO0077', 'COO0078', 'COO0079', 'COO0080', 'COO0081', 'COO0082', 'COO0083', 'COO0084', 'COO0085', 
                'COO0086', 'COO0087', 'COO0088', 'COO0089', 'COO0090', 'COO0091', 'COO0092', 'COO0093', 'COO0094', 
                'COO0095', 'COO0096', 'COO0097', 'COO0098', 'COO0099', 'COO0100', 'COO0101', 'COO0102', 'COO0103', 
                'COO0104', 'COO0105', 'COO0106', 'COO0107', 'COO0108', 'COO0109', 'COO0110', 'COO0111', 'COO0112', 
                'COO0113', 'COO0114', 'COO0115', 'COO0116', 'COO0117', 'COO0118', 'COO0119', 'COO0120', 'COO0121', 
                'COO0122', 'COO0123', 'COO0124', 'COO0125', 'COO0126', 'COO0127', 'COO0128', 'COO0129', 'COO0130', 
                'COO0131', 'COO0132', 'COO0133', 'COO0134', 'COO0135', 'COO0136', 'COO0137', 'COO0138', 'COO0139', 
                'COO0140', 'COO0141', 'COO0142', 'COO0143', 'COO0144', 'COO0145', 'COO0146', 'COO0147', 'COO0148', 
                'COO0149', 'COO0150', 'COO0151', 'COO0152', 'COO0153', 'COO0154', 'COO0155', 'COO0156', 'COO0157', 
                'COO0158', 'COO0159', 'COO0160', 'COO0161', 'COO0162', 'COO0163', 'COO0164', 'COO0165', 'COO0166', 
                'COO0167', 'COO0168', 'COO0169', 'COO0170', 'COO0171', 'COO0172', 'COO0173', 'COO0174', 'COO0175', 
                'COO0176', 'COO0177', 'COO0178', 'COO0179', 'COO0180', 'COO0181', 'COO0182', 'COO0183', 'COO0184', 
                'COO0185', 'COO0186', 'COO0187', 'COO0188', 'COO0189', 'COO0190', 'COO0191', 'COO0192', 'COO0193', 
                'COO0194', 'COO0195', 'COO0196', 'COO0197', 'COO0198', 'COO0199', 'COO0200', 'COO0201', 'COO0202', 
                'COO0203', 'COO0204', 'COO0205', 'COO0206', 'COO0207', 'COO0208', 'COO0209', 'COO0210', 'COO0211', 
                'COO0212', 'COO0213', 'COO0214', 'COO0215', 'COO0216', 'COO0217', 'COO0218', 'COO0219', 'COO0220', 
                'COO0221', 'COO0222', 'COO0223', 'COO0224', 'COO0225', 'COO0226', 'COO0227', 'COO0228', 'COO0229', 
                'COO0230', 'COO0231', 'COO0232', 'COO0233', 'COO0234', 'COO0235', 'COO0236', 'COO0237', 'COO0238', 
                'COO0239', 'COO0240', 'COO0241', 'COO0242', 'COO0243', 'COO0244', 'COO0245', 'COO0246', 'COO0247', 
                'COO0248', 'COO0249', 'COO0250', 'COO0251', 'COO0252', 'COO0253', 'COO0254', 'COO0255', 'COO0256', 
                'COO0257', 'COO0258', 'COO0259', 'COO0260', 'COO0261', 'COO0262', 'COO0263', 'COO0264', 'COO0265', 
                'COO0266', 'COO0267', 'COO0268', 'COO0269', 'COO0270', 'COO0271', 'COO0272', 'COO0273', 'COO0274', 
                'COO0275', 'COO0276', 'COO0277', 'COO0278', 'COO0279', 'COO0280', 'COO0281', 'COO0282', 'COO0283', 
                'COO0284', 'COO0285', 'COO0286', 'COO0287', 'COO0288', 'COO0289', 'COO0290', 'COO0291', 'COO0292', 
                'COO0293', 'COO0294', 'COO0295', 'COO0296', 'COO0297', 'COO0298', 'COO0299', 'COO0300', 'COO0301', 
                'COO0302', 'COO0303', 'COO0304', 'COO0305', 'COO0306', 'COO0307', 'COO0308', 'COO0309', 'COO0310', 
                'COO0311', 'COO0312', 'COO0313', 'COO0314', 'COO0315', 'COO0316', 'COO0317', 'COO0318', 'COO0319', 
                'COO0320', 'COO0321', 'COO0322', 'COO0323', 'COO0324', 'COO0325', 'COO0326', 'COO0327', 'COO0328', 
                'COO0329', 'COO0330', 'COO0331', 'COO0332', 'COO0333', 'COO0334', 'COO0335', 'COO0336', 'COO0337', 
                'COO0338', 'COO0339', 'COO0340', 'COO0341', 'COO0342', 'COO0343', 'COO0344', 'COO0345', 'COO0346', 
                'COO0347', 'COO0348', 'COO0349', 'COO0350', 'COO0351', 'COO0352', 'COO0353', 'COO0354', 'COO0355', 
                'COO0356', 'COO0357', 'COO0358', 'COO0359', 'COO0360', 'COO0361', 'COO0362', 'COO0363', 'COO0364', 
                'COO0365', 'COO0366', 'COO0367', 'COO0368', 'COO0369', 'COO0370', 'COO0371', 'COO0372', 'COO0373', 
                'COO0374', 'COO0375', 'COO0383', 'COO0384', 'COO0385', 'COO0386', 'COO0387', 'COO0413', 'COO0410', 'COO0412'))'''

# ==============================================================================
# QUERIES PARA CAPA "PUNTO DE CARGA"
# ==============================================================================

# Puntos de carga desconectados (sin alimentador) que no son fotovoltaicos ni subtipo 9 (alto voltaje)
CIS_PC20 = '''((ALIMENTADORID is Null) OR (ALIMENTADORID  = '') ) AND 
                ((FUENTEENERGIA  <> 'Fotovoltaico') or (FUENTEENERGIA is null)) and (SUBTIPO <> 9)'''

# Puntos de carga de Media Tensión (subtipo 8) conectados pero sin relación
# a un transformador de distribución en la tabla PuestoTransfDistribucion
CIS_PC21 = '''((((FUENTEENERGIA NOT IN ( 'Fotovoltaico', 'Biomasa', 'E_lica', 'Mini Hidr_ulica' )) or 
                (FUENTEENERGIA is null)) and (SUBTIPO = 8))) and PARENTCIRCUITSOURCEGUID not in 
                (select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                WHERE PD.CIRCUITSOURCEGUID   IS NOT NULL)'''

# Puntos de carga con alimentador pero sin PARENTCIRCUITSOURCEGUID
# (conectados al alimentador pero sin referencia al circuito fuente del trafo)
CIS_PC21_1 = '''(ALIMENTADORID IS NOT NULL AND (FUENTEENERGIA = ('Convencional') OR (FUENTEENERGIA is null))) AND 
                PARENTCIRCUITSOURCEGUID IS NULL'''

# Puntos de carga sin Provincia, Cantón o Parroquia
CIS_PC22 = CIS_ProvCantParr

# Puntos de carga sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_PC22_1 = CIS_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA TABLA "CONEXIÓN CONSUMIDOR"
# ==============================================================================

# Conexiones con circuitos nulos o en minúsculas, vinculadas a puntos de carga
# con alimentador activo y fuente convencional (deben tener circuitos válidos en mayúsculas)
CIS_CC23 = '''((CIRCUITOS IS NULL) OR (CIRCUITOS IN  ('a','b','c','ab','ac','bc','abc','f1','f2','f12'))) 
                AND (PUNTOCARGAGLOBALID IN (select PC.GLOBALID FROM SIGELEC.puntocarga PC WHERE 
                (PC.ALIMENTADORID is not null and ((PC.FUENTEENERGIA  <> 'Fotovoltaico') or (PC.FUENTEENERGIA is null)))))'''

# Conexiones con circuitos F1, F2, F12 (monofásico) vinculadas a trafos
# que NO son monofásicos ni bancos 2F (subtipos distintos de 1,2,3,4,9,10)
CIS_CC24 = '''CIRCUITOS IN ('F1', 'F2', 'F12') AND PUNTOCARGAGLOBALID IN(select PC.GLOBALID from SIGELEC.puntocarga PC 
                WHERE PC.PARENTCIRCUITSOURCEGUID IN(select PD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion PD 
                where PD.SUBTIPO NOT IN (1, 2, 3, 4,9,10)))'''

# Conexiones sin Provincia, Cantón o Parroquia
CIS_CC25 = CIS_ProvCantParr

# Conexiones con circuitos multifásicos (A,B,C,AB,BC,AC,ABC) vinculadas a bancos 2F (9,10)
# con estructura en paralelo ('1B' o '1V') - circuitos incompatibles
CIS_CC26 = '''(CIRCUITOS IN ('A', 'B', 'C','AB','BC', 'AC','ABC') AND PUNTOCARGAGLOBALID IN (select PC.GLOBALID 
                from SIGELEC.puntocarga PC WHERE PC.PARENTCIRCUITSOURCEGUID IN (select TD.CIRCUITSOURCEGUID 
                FROM SIGELEC.PuestoTransfDistribucion TD where TD.SUBTIPO IN (9,10) and TD.CODIGOESTRUCTURA in 
                (select CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE 
                where (CE.DESCRIPCIONCORTA LIKE '1B%' OR CE.DESCRIPCIONCORTA LIKE '1V%')))))'''

# Conexiones con circuitos diferentes de multifásicos vinculadas a bancos 2F (9,10)
# con estructura que NO es paralelo (no '1B' ni '1V')
CIS_CC27 = '''(CIRCUITOS not IN ('A', 'B', 'C','AB','BC', 'AC','ABC') AND PUNTOCARGAGLOBALID IN (select PC.GLOBALID 
                from SIGELEC.puntocarga PC WHERE PC.PARENTCIRCUITSOURCEGUID IN 
                (select TD.CIRCUITSOURCEGUID FROM SIGELEC.PuestoTransfDistribucion TD where TD.SUBTIPO IN (9,10) and 
                TD.CODIGOESTRUCTURA in (select CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE where 
                (CE.DESCRIPCIONCORTA not LIKE '1B%' and CE.DESCRIPCIONCORTA not LIKE '1V%')))))'''

# Conexiones con circuitos multifásicos conectadas a trafos que NO son trifásicos,
# bancos ni bifásicos (subtipos fuera de 5-16)
CIS_CC28 = '''CIRCUITOS IN ('A', 'B', 'C','AB','BC', 'AC','ABC') AND PUNTOCARGAGLOBALID IN (select PC.GLOBALID 
                from SIGELEC.puntocarga PC WHERE PC.PARENTCIRCUITSOURCEGUID IN (select TD.CIRCUITSOURCEGUID FROM 
                SIGELEC.PuestoTransfDistribucion TD where TD.SUBTIPO NOT IN (5, 6, 7, 8, 9, 10,11, 12,13, 14, 15, 16)))'''

# Conexiones sin relación a un punto de carga existente en la tabla PuntoCarga
CIS_CC29 = "(PUNTOCARGAGLOBALID NOT IN (select PC.GLOBALID FROM SIGELEC.puntocarga PC WHERE PC.GLOBALID IS NOT NULL))"

# Conexiones con código único repetido (más de un registro con el mismo CODIGOUNICO)
CIS_CC29_1 = '''codigounico in (select t.codigounico from SIGELEC.CONEXIONCONSUMIDOR t 
                group by t.CODIGOUNICO having count(*) > 1)'''

# Conexiones con circuitos que no son válidos (no son A,B,C,AB,BC,AC,ABC,F1,F2,F12)
# y están vinculadas a puntos de carga con alimentador activo y fuente convencional
CIS_CC29_2 = '''CIRCUITOS  not IN ('A', 'B', 'C','AB','BC', 'AC','ABC', 'F1', 'F2', 'F12') AND 
                (PUNTOCARGAGLOBALID IN (select GLOBALID FROM SIGELEC.PuntoCarga WHERE 
                (ALIMENTADORID is not null and ((FUENTEENERGIA  <> 'Fotovoltaico') or (FUENTEENERGIA is null)))))'''

# Conexiones sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_CC29_3 = CIS_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "LUMINARIA"
# ==============================================================================

# Luminarias desconectadas (sin fase de conexión) que no son fotovoltaicas
CIS_LUM_30 = "(FASECONEXION is Null) AND (FUENTEENERGIA <> 'Fotovoltaico' or FUENTEENERGIA IS NULL)"

# Luminarias con fase de conexión trifásica (7) - normalmente las luminarias son monofásicas
CIS_LUM_31 = "FASECONEXION = 7"

# Luminarias con días de funcionamiento al mes diferente de los valores esperados (100, 43, 21)
CIS_LUM_32 = "DIASFUNCMES NOT IN (100, 43, 21)"

# Luminarias tipo SNP (Sistema Nacional Público - Tipo 'C' en catálogo):
# las horas de funcionamiento 1 deben ser 3, 4, 5, 12 o 24 y horas func. 2 debe ser 0
CIS_LUM_33 = '''(HORASFUNC1 not in (3, 4, 5, 12, 24) or (HORASFUNC1 is null ) or (HORASFUNC2 <> 0 )) and 
                CODIGOESTRUCTURA IN (select CODIGOESTRUCTURA CE from SIGELEC.CATALOGOESTRUCTURA CE where TIPO = 'C')'''

# Luminarias tipo DNP (Doble Nivel de Potencia - Tipo 'D' en catálogo):
# horas func. 1 debe ser 6 o 4, y horas func. 2 debe ser 6 u 8
CIS_LUM_34 = '''(HORASFUNC1 not in (6,4) or (HORASFUNC1 is null ) or (HORASFUNC2 not in (6,8) or HORASFUNC2 is null)) 
                and CODIGOESTRUCTURA IN (select CODIGOESTRUCTURA CE from SIGELEC.CATALOGOESTRUCTURA CE where TIPO = 'D')'''

# Luminarias sin Provincia, Cantón o Parroquia
CIS_LUM_35 = CIS_ProvCantParr

# Luminarias conectadas con alimentador pero sin relación al transformador de distribución
CIS_LUM_36 = '''((((FUENTEENERGIA NOT IN ( 'Fotovoltaico', 'Biomasa', 'E_lica', 'Mini Hidr_ulica' )) or 
                (FUENTEENERGIA is null)))) and PARENTCIRCUITSOURCEGUID not in (select CIRCUITSOURCEGUID TD 
                FROM SIGELEC.PuestoTransfDistribucion TD WHERE TD.CIRCUITSOURCEGUID IS NOT NULL)'''

# Luminarias con código de estructura nulo o vacío
CIS_LUM_37 = "CODIGOESTRUCTURA IS Null or CODIGOESTRUCTURA = '' "

# Luminarias con código de estructura que no existe en el catálogo de estructuras
CIS_LUM_38 = "CODIGOESTRUCTURA NOT IN ( select CODIGOESTRUCTURA CE from SIGELEC.CATALOGOESTRUCTURA CE)"

# Luminarias donde la suma de horas de funcionamiento (func1 + func2) no es igual a 12
CIS_LUM_39 = "((COALESCE(HORASFUNC1,0) )+(COALESCE( HORASFUNC2,0))) <> 12"

# Luminarias sin fecha de registro (creación)
CIS_LUM_39_1 = "FECHAREGISTRO IS NULL or FECHAREGISTRO = ''"

# Luminarias con campo "bajo medición" nulo o vacío
CIS_LUM_39_2 = "BAJOMEDICION IS NULL OR BAJOMEDICION = ''"

# Luminarias sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_LUM_39_3 = CIS_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "PUESTO PROTECCIÓN DINÁMICO"
# ==============================================================================

# Cabecera de alimentador desconectada: dispositivo que es cabecera (en CircuitoFuente)
# pero no tiene alimentador asignado
CIS_PPD40 = '''((SUBTIPO is not null) and GLOBALID in (select CF.PUESTOPROTDINAMGLOBALID FROM SIGELEC.CIRCUITOFUENTE CF 
                WHERE CF.PUESTOPROTDINAMGLOBALID IS NOT NULL)) and ALIMENTADORID is null'''

# Cabecera sin Provincia, Cantón o Parroquia
CIS_PPD41 = CIS_ProvCantParr

# Cabecera sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_PPD41_1 = CIS_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "SUBESTACIÓN"
# ==============================================================================

# Subestaciones sin Provincia, Cantón o Parroquia
CIS_SUB42 = CIS_ProvCantParr

# Subestaciones sin número de subestación o con número vacío
CIS_SUB43 = "NUMEROSUBESTACION is null or NUMEROSUBESTACION = '' "

# Subestaciones con voltaje primario fuera de los valores estándar
# (500kV, 230kV, 138kV, 69kV, 46kV, 34.5kV, 22kV, 22.8kV)
CIS_SUB44 = "VPRIMARIO not in (500000,230000,138000,69000,46000,34500,22000,22800) or VPRIMARIO is null"

# Subestaciones donde el nombre no coincide con el número de subestación
CIS_SUB44_1 = "NOMBRE <> NUMEROSUBESTACION"

# Subestaciones con nombre repetido
CIS_SUB44_2 = '''NOMBRE in (select T.NOMBRE from SIGELEC.subestacion T 
                group by T.NOMBRE having count(*) > 1)'''

# Subestaciones con número repetido
CIS_SUB44_3 = '''NUMEROSUBESTACION in (select T.NUMEROSUBESTACION from SIGELEC.subestacion T 
                group by T.NUMEROSUBESTACION having count(*) > 1)'''

# Subestaciones sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_SUB44_4 = CIS_ConsistenciaProvCantParr

# ==============================================================================
# QUERIES PARA CAPA "TRANSFORMADOR DE DISTRIBUCIÓN"
# ==============================================================================

# Transformadores sin Provincia, Cantón o Parroquia
CIS_TD45 = CIS_ProvCantParr

# Transformadores desconectados (sin alimentador)
CIS_TD46 = "((ALIMENTADORID  is Null) OR (ALIMENTADORID  = '') )"

# Transformadores con subtipo no válido (debe ser 1-16)
CIS_TD46_1 = "(subtipo not in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))"

# Transformadores monofásicos (subtipo 1,2,3,4) con voltaje secundario diferente de 240V
CIS_TD47 = "SUBTIPO in (1,2,3,4 ) AND (COALESCE( VOLTAJESECUNDARIO ,0)) <> 240"

# Transformadores trifásicos (subtipo 5,6,7,8) con voltaje secundario no válido
# (debe ser 220, 380, 440, 400, 480 o 460V)
CIS_TD48 = "SUBTIPO in (5,6,7,8) AND VOLTAJESECUNDARIO NOT IN (220,380,440,400,480,460)"

# Transformadores banco 2F (subtipo 9,10) con voltaje secundario diferente de 240V
CIS_TD49 = "SUBTIPO in (9,10) AND VOLTAJESECUNDARIO <> 240 "

# Transformadores banco 3F (subtipo 11,12) con voltaje secundario diferente de 208V
CIS_TD50 = "SUBTIPO in (11,12) AND VOLTAJESECUNDARIO <> 208"

# Transformadores bifásicos (subtipo 13,14,15,16) con voltaje secundario diferente de 240V
CIS_TD51 = "SUBTIPO in (13,14,15,16) AND VOLTAJESECUNDARIO <> 240"

# Transformadores con voltaje secundario nulo o vacío
CIS_TD51_1 = "VOLTAJESECUNDARIO IS Null or VOLTAJESECUNDARIO = ''"

# Transformadores sin relación a unidad de transformador en la tabla UnidadTransfDistribucion
CIS_TD52 = '''(SUBTIPO is not null) and GLOBALID not in (select UT.PUESTOTRANSFDISTGLOBALID 
                FROM SIGELEC.UNIDADTRANSFDISTRIBUCION UT WHERE UT.PUESTOTRANSFDISTGLOBALID IS NOT NULL)'''

# Transformadores con propiedad diferente de 'PARTICULAR' o 'COD_EMPRESA'
CIS_TD53 = "PROPIEDAD NOT  IN ('PARTICULAR', 'COD_EMPRESA')"

# Transformadores con número de trafo que contiene caracteres no válidos
# (se usa TRANSLATE para detectar caracteres fuera del rango alfanumérico permitido)
CIS_TD54 = '''TRAFO IN (select TRAFO FROM (select TRAFO, CASE WHEN LENGTH(TRIM(TRANSLATE
                (TRAFO, ' abcdefghijklmnopqrstuvwxyz.ABCDEFGHIJKLMNOPQRSTUVWXYZ;/-_0123456789()', ' '))) IS NULL 
                THEN 'VALIDO' ELSE 'NOVALIDO' END AS TIPO from SIGELEC.PUESTOTRANSFDISTRIBUCION ) WHERE TIPO='NOVALIDO') '''

# Transformadores sin consistencia jerárquica entre Provincia, Cantón y Parroquia
CIS_TD54_1 = CIS_ConsistenciaProvCantParr

# Transformadores sin código de estructura
CIS_TD54_2 = "CODIGOESTRUCTURA is null"

# Transformadores cuya potencia (POTENCIAKVA) difiere de la potencia registrada
# en el catálogo de estructuras para su código de estructura
CIS_TD54_3 = '''CODIGOESTRUCTURA IN (SELECT CE.CODIGOESTRUCTURA FROM SIGELEC.CATALOGOESTRUCTURA CE 
                WHERE POTENCIAKVA <> CE.POTENCIA)'''

# Transformadores (no bancos) cuyo código de estructura en el puesto difiere
# del código de estructura de su unidad en la tabla UnidadTransfDistribucion
CIS_TD54_4 = '''GLOBALID  in (select  u.PUESTOTRANSFDISTGLOBALID FROM SIGELEC.UNIDADTRANSFDISTRIBUCION u 
                WHERE ( CODIGOESTRUCTURA  IN  (select CODIGOESTRUCTURA from SIGELEC.UNIDADTRANSFDISTRIBUCION 
                WHERE u.CODIGOESTRUCTURA <> CODIGOESTRUCTURA))) and SUBTIPO not IN (9,10,11,12)'''

# ==============================================================================
# QUERIES PARA TABLA "UNIDAD TRANSFORMADOR"
# ==============================================================================

# Unidades con código de unidad (sticker) que contiene caracteres no válidos
CIS_UT54_5 = '''CODIGOUNIDAD IN (select CODIGOUNIDAD FROM (select CODIGOUNIDAD, CASE WHEN LENGTH(TRIM(TRANSLATE
                (CODIGOUNIDAD, ' abcdefghijklmnopqrstuvwxyz.ABCDEFGHIJKLMNOPQRSTUVWXYZ;/-_0123456789()', ' '))) 
                IS NULL THEN 'VALIDO' ELSE 'NOVALIDO' END AS TIPO from SIGELEC.UNIDADTRANSFDISTRIBUCION) 
                WHERE TIPO='NOVALIDO')'''

# Unidades de transformador sin código de estructura
CIS_UT54_6 = "CODIGOESTRUCTURA IS NULL"

# ==============================================================================
# QUERIES PARA TABLA "ATRIBUTOS CONSUMIDOR"
# ==============================================================================

# Validación de cantidad de conductores (CDACON) según la cantidad de fases (CDAFAS):
# - 1 fase: conductores válidos 1,2,3,4
# - 2 fases: conductores válidos 2,3,4,5
# - 3 fases: conductores válidos 3,4,5
# - 0 fases: conductores válidos solo 0
# Solo aplica para estados activos (EDCCOD: A,B,C,D,H,K,L,M,P,R,Z)
CIS_AT74 = '''((CDAFAS = 1 AND CDACON NOT IN (1,2,3,4)) or (CDAFAS = 2 AND CDACON NOT IN (2,3,4,5)) 
                or (CDAFAS = 3 AND CDACON NOT IN(3,4,5)) or (CDAFAS = 0 AND CDACON NOT IN (0))) 
                and ( EDCCOD = 'A' OR EDCCOD = 'B' OR EDCCOD = 'C' OR EDCCOD = 'D' OR EDCCOD = 'H' OR 
                EDCCOD = 'K' OR EDCCOD = 'L' OR EDCCOD = 'M' OR EDCCOD = 'P' OR EDCCOD = 'R' OR EDCCOD = 'Z')'''

# Consumidores activos con cantidad de fases o conductores en NULL
CIS_AT75 = '''((CDAFAS IS NULL OR CDACON IS NULL)) and (EDCCOD = 'A' OR EDCCOD = 'B' OR EDCCOD = 'C' OR EDCCOD = 'D' 
                OR EDCCOD = 'H' OR EDCCOD = 'K' OR EDCCOD = 'L' OR EDCCOD = 'M' OR EDCCOD = 'P' OR EDCCOD= 'R' 
                OR EDCCOD = 'Z')'''

# Consumidores activos con 0 fases y 0 conductores, pero conectados a un punto de carga
# con alimentador y fuente convencional (no deberían tener fases/conductores en 0)
CIS_AT76 = '''((CDAFAS = 0 AND CDACON = 0) and CODIGOUNICO IN (select C.CODIGOUNICO from SIGELEC.CONEXIONCONSUMIDOR C 
                where C.PUNTOCARGAGLOBALID in (select P.GLOBALID from SIGELEC.PUNTOCARGA P where 
                (P.ALIMENTADORID IS NOT NULL AND (P.FUENTEENERGIA = 'Convencional' OR P.FUENTEENERGIA IS NULL))))) 
                and (EDCCOD = 'A' OR EDCCOD = 'B' OR EDCCOD = 'C' OR EDCCOD = 'D' OR EDCCOD = 'H' OR EDCCOD = 'K' 
                OR EDCCOD = 'L' OR EDCCOD = 'M' OR EDCCOD = 'P' OR EDCCOD = 'R' OR EDCCOD = 'Z')'''

# Consumidores activos donde fases = 0 o conductores = 0 (al menos uno en cero)
CIS_AT76_1 = '''(CDAFAS = 0 OR CDACON = 0) AND (EDCCOD = 'A' OR EDCCOD = 'B' OR EDCCOD = 'C' OR EDCCOD = 'D' 
                OR EDCCOD = 'H' OR EDCCOD = 'K' OR EDCCOD = 'L' OR EDCCOD = 'M' OR EDCCOD = 'P' OR EDCCOD = 'R' 
                OR EDCCOD = 'Z')'''

# Consumidores con cantidad de fases fuera del rango válido (0, 1, 2, 3)
CIS_AT76_2 = "CDAFAS NOT IN (0,1,2,3)"

# Consumidores con cantidad de conductores mayor a 4
CIS_AT76_3 = "CDACON > 4"

# Consumidores con 0 fases pero conductores entre 1 y 4 (inconsistencia)
CIS_AT76_4 = "CDAFAS = 0 AND (CDACON < 5 AND CDACON > 0)"

# Consumidores con código único que no tiene exactamente 10 caracteres
CIS_AT76_5 = "length (CODIGOUNICO )>10 OR length (CODIGOUNICO ) < 10"

# Consumidores con código único nulo
CIS_AT76_6 = "CODIGOUNICO IS NULL"


# ==============================================================================
# DICCIONARIOS DE VALIDACIÓN POR CAPA (Layers)
# ==============================================================================
# Cada diccionario agrupa las queries por capa/tabla del GIS.
# La clave es un identificador descriptivo y el valor es la query SQL.
# El motor de reportes (generarReporte20.py) itera sobre estos diccionarios
# para ejecutar cada validación y contabilizar errores.
# ==============================================================================

# --- Punto de Carga ---
QuerysPuntoCarga =      {'CIS_20_PC_Desconectado': CIS_PC20,
                        'CIS_21_PC_Conectado Sin Relacion Trafo': CIS_PC21,
                        'CIS_21_1_PC_Conectado Sin PARENTCIRCUIT': CIS_PC21_1,
                        'CIS_22_PC_Provincia Canton Parroquia': CIS_PC22,
                        'CIS_22_1_PC_No existe Consistencia Entre Provincia Canton Parroquia': CIS_PC22_1}

# --- Luminaria ---
QuerysLuminaria =       {'CIS_30_LUM_Desconectadas': CIS_LUM_30,
                        'CIS_31_LUM_Trifasica': CIS_LUM_31,
                        'CIS_32_LUM_Dias De Funcionamiento': CIS_LUM_32,
                        'CIS_33_LUM_SNP Horas de Funcionamiento': CIS_LUM_33,
                        'CIS_34_LUM_DNP Horas de Funcionamiento': CIS_LUM_34,
                        'CIS_35_LUM_Provincia Canton Parroquia': CIS_LUM_35,
                        'CIS_36_LUM_Conectada con Alimentador sin Relacion al Transformador': CIS_LUM_36,
                        'CIS_37_LUM_Codigo Estructura Null o Vacio': CIS_LUM_37,
                        'CIS_38_LUM_Codigo Estructura CatalogoEstructura': CIS_LUM_38,
                        'CIS_39_LUM_Suma Horas de Funcionamiento': CIS_LUM_39,
                        'CIS_39_1_LUM_Sin Fecha de Creacion': CIS_LUM_39_1,
                        'CIS_39_2_LUM_Bajo Medicion en Null': CIS_LUM_39_2,
                        'CIS_39_3_LUM_No Existe Consistencia Entre Provincia Canton Parroquia': CIS_LUM_39_3}

# --- Transformador de Distribución ---
QuerysPuestoTransformador = {'CIS_45_TD_Provincia Canton Parroquia': CIS_TD45,
                            'CIS_46_TD_Desconectado': CIS_TD46,
                            'CIS_46_1_TD_Subtipo Valido': CIS_TD46_1,
                            'CIS_47_TD_Voltaje Secundario Monofasico 240V': CIS_TD47,
                            'CIS_48_TD_Voltaje Secundario Trifasico 220V_380_440V_400V_480V': CIS_TD48,
                            'CIS_49_TD_Voltaje Secundario Banco 2F 240V': CIS_TD49,
                            'CIS_50_TD_Voltaje Secundario Banco 3F 208V': CIS_TD50,
                            'CIS_51_TD_Voltaje Secundario Bifasico 240V': CIS_TD51,
                            'CIS_51_1_TD_Voltaje Null o Vacio': CIS_TD51_1,
                            'CIS_52_TD_Unidad Transformador': CIS_TD52,
                            'CIS_53_TD_Propiedad': CIS_TD53,
                            'CIS_54_TD_Numero de Transformador Valido': CIS_TD54,
                            'CIS_54_1_TD_No Existe Consistencia Entre Provincia Canton Parroquia': CIS_TD54_1,
                            'CIS_54_2_TD_Codigo de Estructura Null': CIS_TD54_2,
                            'CIS_54_3_TD_Potencia Deacuerdo a Codigo Estructura': CIS_TD54_3,
                            'CIS_54_4_TD_Estructura Diferente al Codigo Unidad Sin Bancos': CIS_TD54_4}

# --- Regulador de Tensión (vacío - sin validaciones CIS) ---
QuerysReguladorTension =    {

}

# --- Seccionador Cuchilla (vacío - sin validaciones CIS) ---
QuerysSeccionadorCuchilla = {

}

# --- Protección Dinámica ---
QuerysProteccionDinamico =      {'CIS_40_PPD_Cabecera Desconectado': CIS_PPD40,
                                'CIS_41_PPD_Cabecera Provincia Canton Parroquia': CIS_PPD41,
                                'CIS_41_1_PPD_no existe Consistencia Entre Provincia Canton Parroquia': CIS_PPD41_1}

# --- Seccionador Fusible (vacío - sin validaciones CIS) ---
QuerysSeccionadorFusible =  {

}

# --- Semáforo (vacío - sin validaciones CIS) ---
QuerysSemaforo =    {

}

# --- Capacitor (vacío - sin validaciones CIS) ---
QuerysCapacitor =   {

}

# --- Protección BT (vacío - sin validaciones CIS) ---
QuerysProteccionBT = {

}

# --- Transformador de Potencia (vacío - sin validaciones CIS) ---
QuerysTransformadorPotencia = {

}

# --- Punto Vetado (vacío - sin validaciones CIS) ---
QuerysPuntoVetado ={

}

# --- Punto Apertura (vacío - sin validaciones CIS) ---
QuerysPuntoApertura ={

}

# --- Barra (vacío - sin validaciones CIS) ---
QuerysBarra = {

}

# --- Tramos MT (vacío - sin validaciones CIS) ---
QuerysMT = {

}

# --- Tramos BT Aéreo (Acometidas aéreas, subtipos 7,8,9) ---
QuerysBTA =     {'CIS_01_BTA_Acometidas Bifasicas y Trifasicas': CIS_BT01,
                'CIS_02_BTA_Acometidas Voltaje 240V Configuracion Conductores Circuito': CIS_BT02,
                'CIS_03_BTA_Acometidas Voltaje 208V 220V Configuracion Conductores Circuito': CIS_BT03,
                'CIS_04_BTA_Acometidas Voltaje 120V 127V Configuracion de Conductores Circuito': CIS_BT04,
                'CIS_05_BTA_Acometidas Voltaje 208V Banco 3 Transformadores': CIS_BT05,
                'CIS_06_BTA_Acometidas Voltaje 120 240V': CIS_BT06,
                'CIS_07_BTA_Acometidas Voltaje 127 220V': CIS_BT07,
                'CIS_08_BTA_Acometidas Configuracion Conductores 2F2C_2F3C_3F3C_3F4': CIS_BT08,
                'CIS_09_BTA_Acometidas Configuracion Conductores 1F3C_1F4C Banco 2 Transformadores': CIS_BT09,
                'CIS_10_BTA_Acometidas Configuracion Conductores 1F3C_1F4C Banco 2 Transformadores Paralelo': CIS_BT10,
                'CIS_11_BTA_Acometidas Configuracion Conductores 1F3C_1F4C': CIS_BT11,
                'CIS_12_BTA_Acometidas Circuito Conductores Banco 2 Transformadores': CIS_BT12,
                'CIS_13_BTA_Acometidas Circuito Conductores Banco 2 Transformadores Monofasicos En Paralelo': CIS_BT13,
                'CIS_14_BTA_Acometidas Circuito Conductores Monofasicos': CIS_BT14,
                'CIS_15_BTA_Acometidas Circuito Conductores Bifasicos': CIS_BT15,
                'CIS_16_BTA_Acometidas Conductor Fase': CIS_BT16,
                'CIS_17_BTA_Acometidas Configuration Conductores': CIS_BT17,
                'CIS_18_BTA_Acometida Aerea Provincia Canton Parroquia': CIS_BT18,
                'CIS_19_BTA_Acometida Circuitos': CIS_BT19,
                'CIS_19_1_BTA_Acometida No Existe Consistencia Entre Provincia Canton Parroquia': CIS_BT19_1,
                'CIS_19_2_BTA_Acometida Calibre': CIS_BT19_2}

# --- Tramos BT Subterráneo (mismas queries que BTA pero con numeración 55-73) ---
QuerysBTS =     {'CIS_55_BTS_Acometidas Bifasicas Y Trifasicas': CIS_BT01,
                'CIS_56_BTS_Acometidas Voltaje 240V_Configuracion Conductores Circuito': CIS_BT02,
                'CIS_57_BTS_Acometidas Voltaje 208V_220V_Configuracion Conductor Circuito': CIS_BT03,
                'CIS_58_BTS_Acometidas Voltaje 120V_127V_Configuracion Conductores Circuito': CIS_BT04,
                'CIS_59_BTS_Acometidas Voltaje 208V_Banco 3 Transformadores': CIS_BT05,
                'CIS_60_BTS_Acometidas Voltaje 120_240V': CIS_BT06,
                'CIS_61_BTS_Acometidas Voltaje 127_220V': CIS_BT07,
                'CIS_62_BTS_Acometidas Configuracion Conductores 2F2C_2F3C_3F3C_3F4': CIS_BT08,
                'CIS_63_BTS_Acometidas Configuracion Conductores 1F3C_1F4C Banco 2 Transformadores': CIS_BT09,
                'CIS_64_BTS_Acometidas Configuracion Conductores 1F3C_1F4C Banco 2 Transformadores Paralelo': CIS_BT10,
                'CIS_65_BTS_Acometidas Configuracion Conductores 1F3C_1F4C': CIS_BT11,
                'CIS_66_BTS_Acometidas Circuito Conductores Banco 2 Transformadores': CIS_BT12,
                'CIS_67_BTS_Acometidas Circuito Conductores Banco 2 Transformadores Monofasicos En Paralelo': CIS_BT13,
                'CIS_68_BTS_Acometidas Circuito Conductores Monofasicos': CIS_BT14,
                'CIS_69_BTS_Acometidas Circuito Conductores Bifasicos': CIS_BT15,
                'CIS_70_BTS_Acometidas Conductor Fase': CIS_BT16,
                'CIS_71_BTS_Acometidas Configuracion Conductores': CIS_BT17,
                'CIS_72_BTS_Acometida Provincia Canton Parroquia': CIS_BT18,
                'CIS_73_BTS_Acometida Circuitos': CIS_BT19,
                'CIS_73_3_BTS_Acometida No Existe Consistencia Entre Provincia Canton Parroquia': CIS_BT19_1,
                'CIS_73_4_BTS_Acometida Calibre': CIS_BT19_2}

# --- Tramos Subtransmisión (vacío - sin validaciones CIS) ---
QuerysTramosST = {

}

# --- Subestación ---
QuerysSubestacion =     {'CIS_42_SUB_Provincia Canton Parroquia': CIS_SUB42,
                        'CIS_43_SUB_Numero': CIS_SUB43,
                        'CIS_44_SUB_Voltaje Primario': CIS_SUB44,
                        'CIS_44_1_SUB_Nombre Diferente de Numero': CIS_SUB44_1,
                        'CIS_44_2_SUB_Nombre Subestacion Repetido': CIS_SUB44_2,
                        'CIS_44_3_SUB_Numero Subestacion Repetido': CIS_SUB44_3,
                        'CIS_44_4_SUB_Acometida No Existe Consistencia Entre Provincia Canton Parroquia': CIS_SUB44_4}

# --- Poste (vacío - sin validaciones CIS) ---
QuerysPoste ={

}

# --- Estructura Subterránea (vacío - sin validaciones CIS) ---
QuerysEstructuraSubterranea = {

}

# --- Tensor (vacío - sin validaciones CIS) ---
QuerysTensor = {

}

# --- Equipos de Telecomunicación (vacío - sin validaciones CIS) ---
QuerysEquipoTelcom = {
                        }

# --- Tramos Telecomunicaciones (vacío - sin validaciones CIS) ---
QuerysTramoTelcom = {
                        }


# ==============================================================================
# DICCIONARIOS DE VALIDACIÓN POR TABLA
# ==============================================================================

# --- Atributos del Consumidor ---
QuerysAtributosConsumidor =     {'CIS_74_AC_Cantidad de conductores dependiendo de la cantidad de fases': CIS_AT74,
                                'CIS_75_AC_Cantidad Fases o Cantidad de Conductores Null': CIS_AT75,
                                'CIS_76_AC_Cantidad Fases o Cantidad de Conductores Cero': CIS_AT76,
                                'CIS_76.1_AC_Cantidad Fases Cero o Cantidad de Conductores Cero': CIS_AT76_1,
                                'CIS_76.2_AC_Cantidad Fases diferentes a 0_1_2_3': CIS_AT76_2,
                                'CIS_76.3_AC_Cantidad Conductores Mayores a 4': CIS_AT76_3,
                                'CIS_76.4_AC_Cantidad Fases Igual a 0 y conductores mayores a 0 y menores a 5': CIS_AT76_4,
                                'CIS_76.5_AC_Cuenta Codigo Unico Cantidad de Caracteres': CIS_AT76_5,
                                'CIS_76.6_AC_Cuenta Codigo Unico en null': CIS_AT76_6}

# --- Conexión Consumidor ---
QuerysConexionConsumidor =      {'CIS_23_CC_Circuitos': CIS_CC23,
                                'CIS_24_CC_Circuito de Trafo Monofasico': CIS_CC24,
                                'CIS_25_CC_Provincia Canton Parroquia': CIS_CC25,
                                'CIS_26_CC_Circuito Banco 2 Transformadores Monofasicos_en_paralelo': CIS_CC26,
                                'CIS_27_CC_Circuito Banco 2 Transformadores': CIS_CC27,
                                'CIS_28_CC_Circuito de Trafo Bifasico Trifasico': CIS_CC28,
                                'CIS_29_CC_Sin Relacion PuntodeCarga': CIS_CC29,
                                'CIS_29_1_CC_Codigo Unico Repetido': CIS_CC29_1,
                                'CIS_29_2_CC_Circuitos II': CIS_CC29_2,
                                'CIS_29_3_CC_No existe Consistencia Entre Provincia Canton Parroquia': CIS_CC29_3}

# --- Unidad Transformador ---
QuerysUTransformador = {'CIS_54_5_UT_Numero de Transformador Valido en Unidad Transformador': CIS_UT54_5,
                        'CIS_54_6_UT_Codigo Estructura null': CIS_UT54_6}

# --- Unidad Capacitor (vacío - sin validaciones CIS) ---
QuerysUCapacitor =  {

}

# --- Circuito Fuente (vacío - sin validaciones CIS) ---
QuerysCircuitoFuente =  {
    
}

# --- Unidad Regulador (vacío - sin validaciones CIS) ---
QuerysURegulador =  {
    
}

# --- Estructura en Poste (vacío - sin validaciones CIS) ---
QuerysEstructuraPoste = {

}

# --- Unidad Fusible (vacío - sin validaciones CIS) ---
QuerysUnidadFusible = {

}

# --- Institución en Poste (vacío - sin validaciones CIS) ---
QuerysInstitucionPoste = {

}

# --- Unidad Protección Dinámica (vacío - sin validaciones CIS) ---
QuerysUnidadProteccionDinamico = {

}

# --- Unidad Transformador Potencia (vacío - sin validaciones CIS) ---
QuerysUnidadTransformadorPotencia = {

}

# --- Detalle Equipo (vacío - sin validaciones CIS) ---
QueryDetalleEquipo = {
                        }

# --- Detalle Tramo (vacío - sin validaciones CIS) ---
QueryDetalleTramo = {
                        }
