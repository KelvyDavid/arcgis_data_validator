# -*- coding: utf-8 -*-
"""
Módulo de Configuración de Capas y Relaciones de Consulta (defaultLayers)
----------------------------------------------------------------------
Este módulo centraliza las variables que definen los nombres y rutas de las capas 
geográficas y tablas de base de datos en ArcGIS (usando el esquema de SIGELEC).
También asocia cada capa con sus correspondientes diccionarios de consultas 
de validación (ADMS, CIS, Enterprise) y mapea las rutas lógicas de ArcGIS a las tablas 
físicas de Oracle en el motor de base de datos.
"""

from QueryDictionaries import ADMS_Querys, CIS_Querys,Enterprise_Querys, Others_Querys

# ==============================================================================
# Variables locales para Capas de "Cable Operadoras"
# ==============================================================================
# Capa que almacena los equipos de telecomunicaciones de cable operadoras en postes
EquipoTelecom = "Cable Operadoras\\EquipoTelecomunicacion"
# Capa para los tramos subterráneos de telecomunicaciones de operadoras
TramoOpSubterraneo = "Cable Operadoras\\TramoOperadoraSubterraneo"
# Capa para los tramos aéreos de telecomunicaciones de operadoras
TramoOpAereo = "Cable Operadoras\\TramoOperadoraAereo"
# Tabla de detalles técnicos de equipos de telecomunicaciones en SIGELEC
DetalleEquipo = "SIGELEC.DETALLEEQUIPO"
# Tabla de detalles de tramos aéreos de telecomunicaciones
DetalleTramoAereo = "SIGELEC.DetalleTramoOperadoraAereo"
# Tabla de detalles de ductos para infraestructura subterránea
DetalleDucto = "SIGELEC.DETALLEDUCTO"

# ==============================================================================
# Variables locales para Capas de "Equipos" (Red Eléctrica)
# ==============================================================================
# Capa de puntos de carga (acometidas de clientes/consumidores)
PuntoCarga = "Equipos\\Punto de Carga"
# Capa de puestos de luminarias de alumbrado público
Luminaria = "Equipos\\Luminaria"
# Capa de puestos de transformadores de distribución (MT a BT)
PuestoTransformador = "Equipos\\Puesto TransfDistribucion"
# Capa de puestos de reguladores de tensión para control de voltaje en MT
ReguladorTension = "Equipos\\Regulador Tension"
# Capa de seccionadores manuales o de cuchilla en media tensión
SeccionadorCuchilla = "Equipos\\Seccionador Cuchilla"
# Capa de puestos de protección dinámica (disyuntores, reconectadores, interruptores)
ProteccionDinamico = "Equipos\\Proteccion Dinamico"
# Capa de seccionadores fusibles (cutouts) para protección de ramales o trafos
SeccionadorFusible = "Equipos\\Seccionador Fusible"
# Capa de pararrayos de protección contra sobretensiones
Pararrayos = "Equipos\\Pararrayo"
# Capa de puestos de capacitores para corrección del factor de potencia
Capacitor = "Equipos\\Capacitor"
# Capa de equipos de protección en baja tensión
ProteccionBT = "Equipos\\Proteccion BT"
# Capa de semáforos de control vial
Semaforo = "Equipos\\Semaforo"
# Capa de puntos vetados o prohibidos para instalación de redes
PuntoVetado = "Equipos\\Punto Vetado"
# Capa de puntos de apertura o corte físico de la red
PuntoApertura = "Equipos\\Punto Apertura"

# ==============================================================================
# Variables locales para Capas de "Tramos" (Red de Conductores)
# ==============================================================================
# Capa de barras de subestación o derivación de conductores
Barra = "Tramos\\Barra"
# Capa de tramos aéreos de conductores de baja tensión (acometidas/red de distribución)
Tramo_BT_Aereo = "Tramos\\Tramo BT Aereo"
# Capa de tramos subterráneos de conductores de baja tensión
Tramo_BT_Subterraneo = "Tramos\\Tramo BT Subterraneo"
# Capa de tramos aéreos de conductores de media tensión (líneas primarias)
Tramo_MT_Aereo = "Tramos\\Tramo MT  Aereo"
# Capa de tramos subterráneos de conductores de media tensión (cables subterráneos MT)
Tramo_MT_Subterraneo = "Tramos\\Tramo MT Subterraneo"
# Capa de tramos aéreos de subtransmisión (alto voltaje, típicamente 69kV)
TramosSubtransmision = "Tramos\\Tramo Subtransmicion Aereo"

# ==============================================================================
# Variables locales para Capas de "Estructuras" (Soporte físico e infraestructura)
# ==============================================================================
# Capa de estructuras subterráneas (cámaras, pozos de revisión)
EstructuraSubterranea = "Estructuras\\Estructura Subterranea"
# Capa de postes de soporte de la red aérea (madera, hormigón, metal, etc.)
Poste = "Estructuras\\Poste"
# Capa de tensores de anclaje para estabilidad de postes
Tensor = "Estructuras\\Tensor"
# Capa de puntos de infraestructura misceláneos
Miscelaneos = "Estructuras\\Miscelaneos"
# Capa que representa las subestaciones de transformación y distribución
Subestacion = "Estructuras\\Subestacion"
# Capa de puestos de transformadores de potencia de subestaciones (Subtransmisión a MT)
TransfPotencia = "Estructuras\\Puesto Transfo Potencia"

# ==============================================================================
# Variables locales para Tablas de "Unidades" (Datos tabulares de equipos)
# ==============================================================================
# Tabla que almacena los atributos comerciales de los clientes y consumidores
AtributoConsumidor = "SIGELEC.ATRIBUTOSCONSUMIDOR"
# Tabla intermedia que relaciona el punto de carga geográfico con el cliente
ConexionConsumidor = "SIGELEC.CONEXIONCONSUMIDOR"
# Tabla de las unidades físicas instaladas en puestos de transformador de distribución
UnidadTranfDist = "SIGELEC.UNIDADTRANSFDISTRIBUCION"
# Tabla de las unidades físicas de capacitores
UnidadCapacitor = "SIGELEC.UNIDADCAPACITOR"
# Tabla del circuito fuente o alimentador eléctrico
CircuitoFuente = "SIGELEC.CIRCUITOFUENTE"
# Tabla de las unidades físicas de reguladores de tensión
UnidadRegulador = "SIGELEC.UNIDADREGULADORTENSION"
# Tabla que asocia las estructuras de montaje físico a cada poste
EstructuraEnPoste = "SIGELEC.ESTRUCTURAENPOSTE"
# Tabla de unidades físicas de fusibles
UnidadFusible = "SIGELEC.UNIDADFUSIBLE"
# Tabla que asocia las instituciones u operadoras que usan un poste
InstitucionEnPoste = "SIGELEC.INSTITUCIONENPOSTE"
# Tabla de unidades físicas de protección dinámica
UnidadProteccionDinamico = "SIGELEC.UNIDADPROTECCIONDINAMICO"
# Tabla de unidades de transformador de potencia en subestaciones
UnidadTransfPot = "SIGELEC.UNIDADTRANSFPOTENCIA"
# Tabla de referencia de dominios y catálogos de ArcGIS
dominiosGIS = "DominiosGIS"

# ==============================================================================
# Lista querysByLayers: Mapeo de Capas a Diccionarios de Consultas SQL
# ==============================================================================
# Cada elemento de la lista es una sublista con la siguiente estructura:
#   [0] Ruta de la Capa / Tabla en ArcGIS
#   [1] Diccionario de queries de validación tipo ADMS (definido en ADMS_Querys.py)
#   [2] Diccionario de queries de validación tipo CIS (definido en CIS_Querys.py)
#   [3] Diccionario de queries de validación tipo Enterprise (definido en Enterprise_Querys.py)
# ==============================================================================
querysByLayers = [
                    # --- Equipos de la Red ---
                    [PuntoCarga, 
                    ADMS_Querys.QuerysPuntoCarga, 
                    CIS_Querys.QuerysPuntoCarga, 
                   Enterprise_Querys.QuerysPuntoCarga],

                    [Luminaria, 
                    ADMS_Querys.QuerysLuminaria, 
                    CIS_Querys.QuerysLuminaria, 
                   Enterprise_Querys.QuerysLuminaria],

                    [PuestoTransformador, 
                    ADMS_Querys.QuerysPuestoTransformador, 
                    CIS_Querys.QuerysPuestoTransformador, 
                   Enterprise_Querys.QuerysPuestoTransformador],

                    [ReguladorTension, 
                    ADMS_Querys.QuerysReguladorTension, 
                    CIS_Querys.QuerysReguladorTension, 
                   Enterprise_Querys.QuerysReguladorTension],

                    [SeccionadorCuchilla, 
                    ADMS_Querys.QuerysSeccionadorCuchilla, 
                    CIS_Querys.QuerysSeccionadorCuchilla, 
                   Enterprise_Querys.QuerysSeccionadorCuchilla],

                    [ProteccionDinamico, 
                    ADMS_Querys.QuerysProteccionDinamico, 
                    CIS_Querys.QuerysProteccionDinamico, 
                   Enterprise_Querys.QuerysProteccionDinamico],

                    [SeccionadorFusible, 
                    ADMS_Querys.QuerysSeccionadorFusible, 
                    CIS_Querys.QuerysSeccionadorFusible, 
                   Enterprise_Querys.QuerysSeccionadorFusible],

                    [Semaforo, 
                    ADMS_Querys.QuerysSemaforo, 
                    CIS_Querys.QuerysSemaforo, 
                   Enterprise_Querys.QuerysSemaforo],

                    [Capacitor, 
                    ADMS_Querys.QuerysCapacitor, 
                    CIS_Querys.QuerysCapacitor, 
                   Enterprise_Querys.QuerysCapacitor],

                    [ProteccionBT, 
                    ADMS_Querys.QuerysProteccionBT, 
                    CIS_Querys.QuerysProteccionBT, 
                   Enterprise_Querys.QuerysProteccionBT],

                    [TransfPotencia, 
                    ADMS_Querys.QuerysTransformadorPotencia, 
                    CIS_Querys.QuerysTransformadorPotencia, 
                   Enterprise_Querys.QuerysTransformadorPotencia],

                    [PuntoVetado, 
                    ADMS_Querys.QuerysPuntoVetado, 
                    CIS_Querys.QuerysPuntoVetado, 
                   Enterprise_Querys.QuerysPuntoVetado],

                    [PuntoApertura, 
                    ADMS_Querys.QuerysPuntoApertura, 
                    CIS_Querys.QuerysPuntoApertura, 
                   Enterprise_Querys.QuerysPuntoApertura],

                    # --- Tramos y Red de Conductores ---
                    [Barra, 
                    ADMS_Querys.QuerysBarra, 
                    CIS_Querys.QuerysBarra, 
                   Enterprise_Querys.QuerysBarra],

                    [Tramo_MT_Aereo, 
                    ADMS_Querys.QuerysMT, 
                    CIS_Querys.QuerysMT, 
                   Enterprise_Querys.QuerysMT],

                    [Tramo_MT_Subterraneo, 
                    ADMS_Querys.QuerysMT, 
                    CIS_Querys.QuerysMT, 
                   Enterprise_Querys.QuerysMT],

                    [Tramo_BT_Aereo, 
                    ADMS_Querys.QuerysBT, 
                    CIS_Querys.QuerysBTA, 
                   Enterprise_Querys.QuerysBT],

                    [Tramo_BT_Subterraneo, 
                    ADMS_Querys.QuerysBT, 
                    CIS_Querys.QuerysBTA, 
                   Enterprise_Querys.QuerysBT],

                    [TramosSubtransmision, 
                    ADMS_Querys.QuerysTramosST, 
                    CIS_Querys.QuerysTramosST, 
                   Enterprise_Querys.QuerysTramosST],

                    # --- Infraestructura de Soporte ---
                    [Subestacion, 
                    ADMS_Querys.QuerysSubestacion, 
                    CIS_Querys.QuerysSubestacion, 
                   Enterprise_Querys.QuerysSubestacion],

                    [Poste, 
                    ADMS_Querys.QuerysPoste, 
                    CIS_Querys.QuerysPoste, 
                   Enterprise_Querys.QuerysPoste],

                    [EstructuraSubterranea, 
                    ADMS_Querys.QuerysEstructuraSubterranea, 
                    CIS_Querys.QuerysEstructuraSubterranea, 
                   Enterprise_Querys.QuerysEstructuraSubterranea],

                    [Tensor, 
                    ADMS_Querys.QuerysTensor, 
                    CIS_Querys.QuerysTensor, 
                   Enterprise_Querys.QuerysTensor],

                    # --- Infraestructura de Telecomunicaciones (Operadoras) ---
                    [EquipoTelecom,
                    ADMS_Querys.QuerysEquipoTelcom,
                    CIS_Querys.QuerysEquipoTelcom,
                   Enterprise_Querys.QuerysEquipoTelcom],

                    [TramoOpAereo,
                    ADMS_Querys.QuerysTramoTelcom,
                    CIS_Querys.QuerysTramoTelcom,
                   Enterprise_Querys.QuerysTramoTelcom],

                    [TramoOpSubterraneo,
                    ADMS_Querys.QuerysTramoTelcom,
                    CIS_Querys.QuerysTramoTelcom,
                   Enterprise_Querys.QuerysTramoTelcom],

                    # --- Tablas de Unidades y Datos Comerciales ---
                    [AtributoConsumidor, 
                    ADMS_Querys.QuerysAtributosConsumidor, 
                    CIS_Querys.QuerysAtributosConsumidor, 
                   Enterprise_Querys.QuerysAtributosConsumidor],

                    [ConexionConsumidor, 
                    ADMS_Querys.QuerysConexionConsumidor, 
                    CIS_Querys.QuerysConexionConsumidor, 
                   Enterprise_Querys.QuerysConexionConsumidor],

                    [UnidadTranfDist, 
                    ADMS_Querys.QuerysUTransformador, 
                    CIS_Querys.QuerysUTransformador, 
                   Enterprise_Querys.QuerysUTransformador],

                    [UnidadCapacitor, 
                    ADMS_Querys.QuerysUCapacitor, 
                    CIS_Querys.QuerysUCapacitor, 
                   Enterprise_Querys.QuerysUnidadCapacitor],

                    [CircuitoFuente, 
                    ADMS_Querys.QuerysCircuitoFuente, 
                    CIS_Querys.QuerysCircuitoFuente, 
                   Enterprise_Querys.QuerysCircuitoFuente],

                    [UnidadRegulador, 
                    ADMS_Querys.QuerysURegulador, 
                    CIS_Querys.QuerysURegulador, 
                   Enterprise_Querys.QuerysUnidadRegulador],

                    [EstructuraEnPoste, 
                    ADMS_Querys.QuerysEstructuraPoste, 
                    CIS_Querys.QuerysEstructuraPoste, 
                   Enterprise_Querys.QuerysEstructuraPoste],

                    [UnidadFusible, 
                    ADMS_Querys.QuerysUnidadFusible, 
                    CIS_Querys.QuerysUnidadFusible, 
                   Enterprise_Querys.QuerysUnidadFusible],

                    [InstitucionEnPoste, 
                    ADMS_Querys.QuerysInstitucionPoste, 
                    CIS_Querys.QuerysInstitucionPoste, 
                   Enterprise_Querys.QuerysInstitucionPoste],

                    [UnidadProteccionDinamico, 
                    ADMS_Querys.QuerysUnidadProteccionDinamico, 
                    CIS_Querys.QuerysUnidadProteccionDinamico, 
                   Enterprise_Querys.QuerysUnidadProteccionDinamico],

                    [UnidadTransfPot, 
                    ADMS_Querys.QuerysUnidadTransformadorPotencia, 
                    CIS_Querys.QuerysUnidadTransformadorPotencia, 
                   Enterprise_Querys.QuerysUnidadTransformadorPotencia],

                    [DetalleEquipo,
                    ADMS_Querys.QueryDetalleEquipo,
                    CIS_Querys.QueryDetalleEquipo,
                   Enterprise_Querys.QueryDetalleEquipo],

                    [DetalleTramoAereo,
                    ADMS_Querys.QueryDetalleTramo,
                    CIS_Querys.QueryDetalleTramo,
                   Enterprise_Querys.QueryDetalleTramo],

                    # [DetalleDucto,
                    # ADMS_Querys.QueryDetalleTramo,
                    # CIS_Querys.QueryDetalleTramo,
                    #Enterprise_Querys.QueryDetalleTramo],
                ]

# ==============================================================================
# Diccionario tablesByLayers: Mapeo de Rutas de Capas de ArcGIS a Tablas Físicas Oracle
# ==============================================================================
# Este diccionario permite asociar las capas lógicas representadas por subcarpetas
# y nombres en los Feature Classes de la Geodatabase de ArcGIS, a sus nombres 
# reales de tablas físicas del esquema SIGELEC en la base de datos Oracle relacional.
# Se usa para resolver subconsultas SQL que comparan datos entre capas físicas.
# ==============================================================================
tablesByLayers = {
                    # --- Equipos y Tramos Telecomunicación ---
                    EquipoTelecom: 'SIGELEC.EQUIPO',
                    TramoOpSubterraneo: 'SIGELEC.TramoOperadoraSubterraneo',
                    TramoOpAereo: 'SIGELEC.TramoOperadoraAereo',

                    # --- Equipos Eléctricos ---
                    PuntoCarga: 'SIGELEC.PUNTOCARGA',
                    Luminaria: 'SIGELEC.LUMINARIA',
                    PuestoTransformador: 'SIGELEC.PUESTOTRANSFDISTRIBUCION',
                    ReguladorTension: 'SIGELEC.PUESTOREGULADORTENSION',
                    SeccionadorCuchilla: 'SIGELEC.PUESTOSECCIONADOR',
                    SeccionadorFusible: 'SIGELEC.PUESTOSECCIONADORFUSIBLE',
                    ProteccionDinamico: 'SIGELEC.PUESTOPROTECCIONDINAMICO',
                    Pararrayos: 'SIGELEC.PARARRAYOS',
                    Capacitor: 'SIGELEC.PUESTOCORRECTORFACTORPOTENCIA',
                    ProteccionBT: 'SIGELEC.PUESTOPROTECCIONBAJATENSION',
                    Semaforo: 'SIGELEC.SEMAFORO',
                    PuntoVetado: 'SIGELEC.PUNTO_VETADO',

                    # --- Tramos y Barra ---
                    Barra: 'SIGELEC.BARRA',
                    Tramo_BT_Aereo: 'SIGELEC.TRAMOBAJATENSIONAEREO',
                    Tramo_BT_Subterraneo: 'SIGELEC.TRAMOBAJATENSIONSUBTERRANEO',
                    Tramo_MT_Aereo: 'SIGELEC.TRAMODISTRIBUCIONAEREO',
                    Tramo_MT_Subterraneo: 'SIGELEC.TRAMODISTRIBUCIONSUBTERRANEO',

                    # --- Infraestructura ---
                    EstructuraSubterranea: 'SIGELEC.ESTRUCTURASUBTERRANEA',
                    Poste: 'SIGELEC.ESTRUCTURASOPORTE',
                    Tensor: 'SIGELEC.TENSOR',
                    Miscelaneos: 'SIGELEC.PUNTOMISCELANEO',
                    Subestacion: 'SIGELEC.SUBESTACION',
                    TransfPotencia: 'SIGELEC.PUESTOTRANSFPOTENCIA',
                }