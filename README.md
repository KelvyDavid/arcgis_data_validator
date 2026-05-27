# ArcGIS Data Validator ⚡🔍

**ArcGIS Data Validator** es una herramienta de automatización y control de calidad diseñada para garantizar la integridad, calidad y consistencia de los datos geográficos y tabulares en bases de datos geográficas de redes de distribución eléctrica (bajo el estándar SIGELEC).

El script ejecuta de manera secuencial y automatizada cientos de consultas de validación SQL sobre _Feature Classes_ (capas geográficas) y tablas relacionales, identificando inconsistencias topológicas, errores de llenado, registros duplicados, inconsistencias comerciales o valores fuera de norma en la infraestructura eléctrica de media y baja tensión.

---

## 🚀 Características Principales

- **Validación Multi-Dominio:** Ejecuta validaciones agrupadas en tres categorías:
  - **ADMS**: Reglas de modelado de red y consistencia de campos técnicos (fases, voltajes, calibres, conductores).
  - **CIS**: Reglas comerciales de acometidas, puntos de carga, clientes y alumbrado público.
  - **Enterprise**: Reglas específicas locales de la empresa.
- **Alto Rendimiento y Eficiencia:** Implementa el cursor de búsqueda optimizado de ArcPy (`arcpy.da.SearchCursor`) que realiza consultas ágiles sin sobrecargar la memoria de la base de datos (Oracle / GDB local) ni bloquear tablas.
- **Resolución de Tablas Físicas:** Traduce las capas geográficas lógicas de ArcGIS a las tablas de base de datos relacionales físicas del esquema SIGELEC en Oracle (por ejemplo, de `Equipos\Punto de Carga` a `SIGELEC.PUNTOCARGA`) para ejecutar cruces relacionales complejos en SQL.
- **Doble Reporte de Salida:**
  - **Reporte Agregado:** Muestra un resumen general con la cantidad de errores encontrados por cada regla y capa.
  - **Detalle de Warnings:** Lista cada elemento que falló la validación indicando su `OBJECTID`, `GLOBALID` y un estado de corrección inicial (por defecto "Pendiente").
- **Compatibilidad:** Mantiene compatibilidad con Python 2.7 (entorno heredado de ArcMap / Catalog) y Python 3 (entorno de ArcGIS Pro).

---

## 📁 Estructura del Repositorio

El proyecto se divide de forma modular para facilitar la edición y mantenimiento de las reglas de negocio sin necesidad de alterar el código del motor de ejecución:

| Archivo / Carpeta                                                                                                                            | Descripción                                                                                                                                                                                                                                               |
| :------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📄 [generarReporte.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/generarReporte.py)                            | **Script Principal**. Recupera los parámetros de ArcGIS, inicializa la exportación a CSV y coordina la iteración de validación llamando a [contarerrores](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/generarReporte.py#L21). |
| 📁 `QueryDictionaries/`                                                                                                                      | Contiene los diccionarios de configuración y las consultas SQL de validación.                                                                                                                                                                             |
| ├─ 📄 [defaultLayers.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/defaultLayers.py)         | Define las variables de capas, el mapeo de nombres a tablas físicas en Oracle y la asociación de diccionarios de consulta para cada capa.                                                                                                                 |
| ├─ 📄 [ADMS_Querys.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/ADMS_Querys.py)             | Consultas SQL de validación técnica orientadas a la red de media y baja tensión para ADMS.                                                                                                                                                                |
| ├─ 📄 [CIS_Querys.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/CIS_Querys.py)               | Consultas SQL de validación orientadas a la relación red-cliente y alumbrado público.                                                                                                                                                                     |
| ├─ 📄 [Enterprise_Querys.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/Enterprise_Querys.py) | Consultas SQL personalizadas para requerimientos específicos de la empresa.                                                                                                                                                                               |
| └─ 📄 [Others_Querys.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/Others_Querys.py)         | Consultas de validación complementarias o en desarrollo.                                                                                                                                                                                                  |

---

## 🛠️ Cómo Funciona la Validación

1. **Entrada de Parámetros:** El usuario ingresa a través del panel de ArcGIS la carpeta de salida y el identificador de la semana de trabajo.
2. **Ejecución de Consultas:** Para cada elemento mapeado en [defaultLayers.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/defaultLayers.py), el script llama a [contarerrores](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/generarReporte.py#L21) pasándole el nombre de la capa, el diccionario de reglas (ADMS, CIS o Enterprise) y la semana.
3. **Escritura en Warnings:** Cada vez que una consulta SQL devuelve registros que cumplen el criterio de error, el script los escribe inmediatamente en el archivo CSV detallado de Warnings.
4. **Cierre de Conexiones:** Se liberan los cursores (`SearchCursor`) de manera explícita en bloques `finally` para evitar bloqueos y fallos de esquema en la base de datos relacional.

### Reportes Generados

Al finalizar, se guardan en la carpeta de destino dos archivos con el sufijo `_DDMMYY.csv` (donde `DDMMYY` es la fecha de ejecución):

#### 1. Resumen de Reporte (`Reporte_DDMMYY.csv`)

Proporciona una vista rápida de la salud de los datos.

- **Columnas:** `Query Name`, `Element`, `Error` (Cantidad de inconsistencias halladas o "Error" si la consulta falló por campos inexistentes).

#### 2. Detalle de Advertencias (`Warnings_DDMMYY.csv`)

Permite a los operadores del GIS ubicar, corregir y dar seguimiento a los registros inconsistentes en la base de datos geográfica.

- **Columnas:** `Fecha`, `Semana`, `Tipo Validacion`, `Layer or Table`, `Query Name`, `OBJECTID`, `GLOBALID`, `EstadoCorreccion` (iniciado en "Pendiente").

---

## ⚙️ Integración en ArcGIS

Para desplegar esta herramienta como un geoprocesamiento interactivo dentro de ArcMap o ArcGIS Pro, siga los siguientes pasos:

1. **Crear una Caja de Herramientas:** Abra _ArcToolbox_ o _Catalog_, haga clic derecho sobre su carpeta de trabajo y seleccione `New > Toolbox` (Caja de herramientas `.tbx`).
2. **Agregar un Nuevo Script:** Haga clic derecho sobre la Toolbox creada y seleccione `Add > Script`.
3. **Configurar el Script:**
   - **General:** Defina un nombre e identificador (ej. `DataValidator`).
   - **Source File:** Seleccione la ruta local del archivo [generarReporte.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/generarReporte.py).
4. **Configurar Parámetros del Script:** En la pestaña _Parameters_, configure los dos parámetros obligatorios requeridos por la herramienta:

| #     | Display Name (Nombre de Pantalla) | Data Type (Tipo de Datos) | Type (Tipo) | Direction (Dirección) |
| :---- | :-------------------------------- | :------------------------ | :---------- | :-------------------- |
| **0** | Carpeta de Salida / Output Folder | Folder                    | Required    | Input                 |
| **1** | Semana / Ciclo de Validación      | String                    | Required    | Input                 |

> [!IMPORTANT]
> El entorno de Python que ejecuta el geoprocesamiento debe tener acceso a las capas geográficas configuradas en [defaultLayers.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/defaultLayers.py) dentro del documento de mapa activo (`.mxd` o `.aprx`) o dentro del espacio de trabajo del ArcSDE (Oracle).

---

## 🧪 Ejemplos de Reglas Validadas

Las consultas SQL son cláusulas `WHERE` que filtran los elementos que **no cumplen** con las reglas del sistema (es decir, capturan los errores):

- **Consistencia de Voltajes (Media Tensión):** Un tramo de MT con subtipo monofásico (1 o 4) debe operar a un voltaje de línea a neutro estándar (ej. 7621V, 13279V), mientras que tramos trifásicos (3 o 6) deben operar a voltajes de línea a línea estándar (ej. 13800V, 22000V).
- **Consistencia Comercial (Acometidas):** Acometidas trifásicas o bifásicas en baja tensión (CIS_BT01) no pueden estar conectadas eléctricamente a transformadores de distribución monofásicos de fase única.
- **Validación del Calibre:** El código del conductor de fase debe pertenecer a un catálogo oficial de conductores normalizados (e.g. `COO0001` al `COO0375`).
- **Nomenclatura ADMS:** Códigos de transformadores (`CODIGOADMS`) deben respetar el formato del subtipo (por ejemplo, `TR_1F_` para transformador monofásico y no tener caracteres especiales como comas o espacios).
- **Integridad Territorial:** Comprobación de que campos geográficos de localización (`PROVINCIA`, `CANTON`, `PARROQUIA`) no estén nulos y mantengan una consistencia en sus códigos jerárquicos (los primeros dígitos del cantón deben corresponder a la provincia, etc.).

---

## 📚 Requisitos Previos

Para ejecutar el script correctamente, debe tener instalado en su entorno de trabajo:

- **ArcGIS Desktop (10.x)** con licencia de **ArcPy** activa (para Python 2.7) O **ArcGIS Pro** (para Python 3).
- **Python** configurado en el PATH (si trabaja fuera del ArcCatalog/ArcMap). La versión dependerá de su instalación de ArcGIS (Python 2.7 o 3.x).
- Acceso a la base de datos **Oracle** o **Enterprise Geodatabase** que contiene el esquema **SIGELEC**, con los permisos de lectura necesarios para ejecutar consultas `SELECT` sobre las capas listadas.

---

## 🤝 Contribuciones

Este proyecto es un esfuerzo de colaboración y mantenimiento de scripts para la calidad de datos geográficos. Las contribuciones son bienvenidas.

- **Agregar o Modificar Consultas:** Las reglas de negocio están centralizadas en diccionarios en la carpeta [QueryDictionaries](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/defaultLayers.py).
  - Para añadir una nueva regla, edite el archivo `.py` correspondiente (ADMS_Querys, CIS_Querys,Enterprise_Querys) añadiendo una nueva entrada al diccionario (ej. `"NUEVA_VALIDACION": "SQL_QUERY_HERE"`).
  - Asegúrese de que la capa correspondiente esté mapeada en [defaultLayers.py](file:///c:/Users/david/OneDrive/Documentos/GitHub/arcgis_data_validator/QueryDictionaries/defaultLayers.py).

---

## 📄 Licencia

Este proyecto es de código cerrado y propiedad de la empresa para la cual fue desarrollado.

---

## 👤 Autor

Desarrollado como herramienta de automatización GIS para la gestión de redes eléctricas, con mantenimiento continuo para asegurar la integridad de los datos. Se mantiene actualizado y optimizado para su uso en entornos de producción de ArcMap y ArcGIS Pro.
