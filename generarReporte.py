# -*- coding: utf-8 -*-
"""
Módulo de Generación de Reportes de Validación GIS
--------------------------------------------------
Este script automatiza el proceso de validación de datos geográficos y tabulares 
en bases de datos geográficas de ArcGIS (usando arcpy). Ejecuta consultas predefinidas
(queries) de validación correspondientes a tres categorías principales:
1. ADMS
2. CIS
3. Enterprise

Las inconsistencias o errores detectados se registran de forma agregada en un 
reporte general de conteos y de forma detallada en un archivo de advertencias (Warnings).
"""

import arcpy
from QueryDictionaries import defaultLayers as ly
import csv
import datetime

def contarerrores(layer, querydictionary, semana, validacion):
    """
    Ejecuta un conjunto de consultas de validación (queries) sobre una capa o tabla específica,
    cuenta los registros inconsistentes y registra los detalles de cada error en los archivos CSV.

    Parámetros:
    -----------
    layer : str
        Ruta o nombre de la capa geográfica o tabla a validar.
    querydictionary : dict
        Diccionario que contiene pares de 'Nombre de la Consulta': 'Sentencia SQL (Query)'.
    semana : str
        Semana de validación especificada por el usuario en la interfaz de ArcGIS.
    validacion : str
        Etiqueta del tipo de validación que se está ejecutando (por ejemplo, 'ADMS', 'CIS', 'Enterprise').
    """
    item = 0
    # Verificar si el diccionario de consultas no está vacío
    if querydictionary:
        # Iterar a través de las consultas ordenadas por su clave descriptiva
        for querykey in sorted(querydictionary.keys()):
            count = 0
            arcpy.AddMessage('Running Query: ' + querykey)

            # Usar arcpy.da.SearchCursor para recuperar de forma eficiente OBJECTID y GLOBALID 
            # de los elementos que cumplen con la condición de error especificada en la consulta SQL.
            with arcpy.da.SearchCursor(layer, ['OBJECTID', 'GLOBALID'], querydictionary[querykey]) as cursor:
                try:
                    for a in cursor:
                        count += 1
                        # Escribir el detalle del error en el archivo de Warnings
                        writerWarnings.writerow([
                            datetime.datetime.now(), 
                            semana, 
                            validacion, 
                            layer, 
                            querykey, 
                            a[0],  # OBJECTID del elemento inconsistente
                            a[1],  # GLOBALID del elemento inconsistente
                            'Pendiente'  # Estado de corrección inicial
                        ])
                except arcpy.ExecuteError:
                    # En caso de que falle la ejecución de la consulta (por ejemplo, campo inexistente)
                    count = 'Error'
                finally:
                    # Garantizar la liberación del cursor para evitar bloqueos en la base de datos
                    del cursor
            
            # Mostrar mensaje con el resultado en la consola de ArcGIS y guardar el resumen
            arcpy.AddMessage('Warnings: ' + str(count))
            writerReport.writerow([querykey, layer, count])

# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---

# Recuperar parámetros de entrada provistos por el usuario desde la caja de herramientas de ArcGIS
# Parámetro 0: Carpeta/Ubicación de salida de los reportes
location = arcpy.GetParameterAsText(0)
# Parámetro 1: Nombre de la semana o ciclo de validación
semana = arcpy.GetParameterAsText(1)

# Configurar nombres de archivos CSV utilizando la fecha actual en formato DDMMYY
fecha = datetime.datetime.today().strftime("%d%m%y")
Report = location + '/Reporte_'+ fecha+ '.csv'
warnings = location + '/Warnings_'+ fecha+ '.csv'

# Abrir los archivos en bloques separados para garantizar compatibilidad con Python 2.7 
# (ambiente estándar para motores antiguos de ArcMap)
with open(Report, 'w') as reportfile:
    # Configurar el escritor de CSV para el reporte resumido
    writerReport = csv.writer(reportfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writerReport.writerow(['Query Name', 'Element', 'Error'])

    with open(warnings, 'w') as warningsfile:
        # Configurar el escritor de CSV para el reporte detallado de advertencias (Warnings)
        writerWarnings = csv.writer(warningsfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writerWarnings.writerow([
            'Fecha', 'Semana', 'Tipo Validacion', 'Layer or Table', 
            'Query Name', 'OBJECTID', 'GLOBALID', 'EstadoCorreccion'
        ])

        # --- VALIDACIONES ADMS ---
        # Ejecuta las consultas de la sección ADMS sobre cada capa y tabla definida en defaultLayers
        for query in ly.querysByLayers:
            contarerrores(query[0], query[1], semana, 'ADMS')

        # --- VALIDACIONES CIS ---
        # Ejecuta las consultas de la sección CIS sobre cada capa y tabla definida en defaultLayers
        for query in ly.querysByLayers:
            contarerrores(query[0], query[2], semana, 'CIS')

        # --- VALIDACIONES de Empresa ---
        # Ejecuta las consultas de la sección Enterprise sobre cada capa y tabla definida en defaultLayers
        for query in ly.querysByLayers:
            contarerrores(query[0], query[3], semana, 'Enterprise')
