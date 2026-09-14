"""
VaquerosGIS
===========
Carga en el proyecto de QGIS una base cartográfica de Tamaulipas:
imagen de satélite de fondo, polígonos (estado, municipios, localidades)
y puntos (localidades, colonias, campus), ya recortados con el límite del
estado y con estilo aplicado.

Datos: Who's On First (https://whosonfirst.org), recortados con el límite de
Tamaulipas. En los polígonos se eliminan los fragmentos de municipios o
localidades vecinas que quedan dentro del estado con menos del 1 % de su
superficie (astillas del recorte). SRC de los datos: EPSG:32614.
"""
import os

from qgis.PyQt.QtGui import QColor, QFont, QPainter
from qgis.core import (
    QgsPalLayerSettings,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayerSimpleLabeling,
    QgsCoordinateTransform,
    QgsBilinearRasterResampler,
    QgsColorRampShader,
    QgsFillSymbol,
    QgsHillshadeRenderer,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsLinePatternFillSymbolLayer,
    QgsMarkerSymbol,
    QgsProject,
    QgsRasterLayer,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)




# Fondo: Google Satellite (teselas XYZ).
BASEMAP_NAME = 'Google Satellite'
BASEMAP_URI = ('type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D'
               '%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=20&zmin=0')

# Relieve: modelo digital de elevaciones (MDE) de Tamaulipas, 84 x 92 m,
# EPSG:32614, recortado con el estado.
DEM_FILE = 'tamaulipas_dem.tif'
DEM_SOURCE = ''  # fuente del MDE, sin determinar (se usa como atribución)
# Tintas hipsométricas suaves: (altura en m, color, etiqueta de la leyenda)
DEM_STOPS = [
    (-15, '#5e8c77', '−15 m'),
    (0, '#6f9f7f', '0 m'),
    (50, '#8fb88f', '50 m'),
    (100, '#aecb9a', '100 m'),
    (200, '#cadba6', '200 m'),
    (400, '#e2e3b1', '400 m'),
    (700, '#e7d4a0', '700 m'),
    (1000, '#d9ba88', '1.000 m'),
    (1500, '#c49b73', '1.500 m'),
    (2000, '#a98267', '2.000 m'),
    (2500, '#9a7e74', '2.500 m'),
    (3000, '#b9aca8', '3.000 m'),
    (3503, '#f4f1ef', '3.503 m'),
]
# Sombreado multidireccional, mezclado por multiplicación sobre los colores.
HILLSHADE_AZIMUTH = 315
HILLSHADE_ALTITUDE = 45
HILLSHADE_ZFACTOR = 1.0
HILLSHADE_OPACITY = 0.55

# Distritos de riego de Tamaulipas (7): sin recortar (geometría oficial).
# Azul celeste, con trama rayada y contorno del mismo color.
DR_LAYER = ('distritos_riego', 'Distritos de riego', '#4fc3f7', '0.6')
DR_HATCH_ANGLE = 45       # grados
DR_HATCH_DISTANCE = 1.5   # mm entre rayas
DR_HATCH_WIDTH = 0.3      # mm de grosor de raya
DR_ATTRIBUTION = ('Distritos de riego: CONAGUA, servicio INFOTECA de SEMARNAT '
                  '(año agrícola 2016-2017)')

WOF_ATTRIBUTION = 'Datos de Who\'s On First (https://whosonfirst.org/docs/licenses/)'

# Color de los municipios: el mismo para el borde y para los nombres.
MUNI_COLOR = '#ffd60a'

# (capa en el GeoPackage, nombre en QGIS, color)
# Orden de la lista = orden en el panel de capas (la primera, arriba).
POINT_LAYERS = [
    ('campus_punto', 'Campus', '#ff00ff'),
    ('colonias_punto', 'Colonias', '#00e5ff'),
    ('localidades_punto', 'Localidades', '#ff3b30'),
]
POINT_SIZE = '0.5'  # mm

# (capa, nombre, color del borde, grosor del borde en mm)
POLYGON_LAYERS = [
    ('estado', 'Estado', '#ffffff', '0.8'),
    ('municipios', 'Municipios', MUNI_COLOR, '0.4'),
    ('localidades_poligono', 'Localidades (áreas)', '#7cfc00', '0.3'),
]



# Toponimia de los municipios: campo, tamaño (puntos) y cursiva.
MUNI_LABEL_FIELD = 'name'
MUNI_LABEL_SIZE = 8
MUNI_LABEL_COLOR = MUNI_COLOR
MUNI_LABEL_BUFFER = '#000000'


def municipality_labels():
    """Etiquetas de los municipios: 8 pt, cursiva, del mismo color que el
    borde de los municipios, con un halo negro fino para que se lean sobre
    la imagen de satélite."""
    font = QFont()
    font.setItalic(True)
    fmt = QgsTextFormat()
    fmt.setFont(font)
    fmt.setSize(MUNI_LABEL_SIZE)
    fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
    fmt.setColor(QColor(MUNI_LABEL_COLOR))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(0.4)
    buf.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    buf.setColor(QColor(MUNI_LABEL_BUFFER))
    fmt.setBuffer(buf)
    settings = QgsPalLayerSettings()
    settings.fieldName = MUNI_LABEL_FIELD
    settings.setFormat(fmt)
    return QgsVectorLayerSimpleLabeling(settings)


def irrigation_symbol(color, outline_width):
    """Relleno rayado (líneas a 45 grados) más contorno, todo del mismo
    color."""
    symbol = QgsFillSymbol.createSimple({
        'style': 'no', 'outline_color': color,
        'outline_width': outline_width, 'outline_width_unit': 'MM'})
    hatch = QgsLinePatternFillSymbolLayer()
    hatch.setLineAngle(DR_HATCH_ANGLE)
    hatch.setDistance(DR_HATCH_DISTANCE)
    hatch.setDistanceUnit(QgsUnitTypes.RenderMillimeters)
    hatch.setLineWidth(DR_HATCH_WIDTH)
    hatch.setLineWidthUnit(QgsUnitTypes.RenderMillimeters)
    hatch.setColor(QColor(color))
    line = hatch.subSymbol()
    if line is not None:
        line.setColor(QColor(color))
        line.setWidth(DR_HATCH_WIDTH)
    symbol.insertSymbolLayer(0, hatch)  # la trama debajo del contorno
    return symbol


def _smooth(layer):
    """Remuestreo bilineal al acercarse y al alejarse: el relieve se ve
    suave, sin escalones de píxel."""
    rf = layer.resampleFilter()
    rf.setZoomedInResampler(QgsBilinearRasterResampler())
    rf.setZoomedOutResampler(QgsBilinearRasterResampler())
    rf.setMaxOversampling(2.0)


def dem_color_layer(path):
    layer = QgsRasterLayer(path, 'Elevación (m)', 'gdal')
    if not layer.isValid():
        return None
    ramp = QgsColorRampShader(DEM_STOPS[0][0], DEM_STOPS[-1][0])
    try:
        ramp.setColorRampType(QgsColorRampShader.Interpolated)
    except AttributeError:  # QGIS recientes
        from qgis.core import Qgis
        ramp.setColorRampType(Qgis.ShaderInterpolationMethod.Linear)
    ramp.setColorRampItemList([
        QgsColorRampShader.ColorRampItem(v, QColor(c), lab)
        for v, c, lab in DEM_STOPS])
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(ramp)
    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    renderer.setClassificationMin(DEM_STOPS[0][0])
    renderer.setClassificationMax(DEM_STOPS[-1][0])
    layer.setRenderer(renderer)
    _smooth(layer)
    return layer


def dem_hillshade_layer(path):
    layer = QgsRasterLayer(path, 'Sombreado', 'gdal')
    if not layer.isValid():
        return None
    renderer = QgsHillshadeRenderer(
        layer.dataProvider(), 1, HILLSHADE_AZIMUTH, HILLSHADE_ALTITUDE)
    renderer.setMultiDirectional(True)
    renderer.setZFactor(HILLSHADE_ZFACTOR)
    renderer.setOpacity(HILLSHADE_OPACITY)
    layer.setRenderer(renderer)
    layer.setBlendMode(QPainter.CompositionMode_Multiply)
    _smooth(layer)
    return layer


def load_tamaulipas_base(iface, plugin_dir, basemap=True, polygons=True,
                         points=True, irrigation=True, relief=False):
    """Carga en el proyecto actual un grupo "Tamaulipas" con las partes
    elegidas: imagen de satélite, relieve, polígonos, distritos de riego y
    puntos.

    Devuelve (cargadas, fallidas): número de capas añadidas y lista de las
    que no se pudieron cargar. Debe ejecutarse en el hilo principal de QGIS
    (toca el proyecto y el lienzo del mapa).
    """
    project = QgsProject.instance()
    gpkg = os.path.join(plugin_dir, 'data', 'tamaulipas_base.gpkg')
    if not os.path.exists(gpkg):
        return 0, ['tamaulipas_base.gpkg']
    if not (basemap or polygons or points or irrigation or relief):
        return 0, []

    # Capa del estado solo como referencia (SRC y encuadre); no se añade
    # al proyecto salvo que se pidan los polígonos.
    ref = QgsVectorLayer(f'{gpkg}|layername=estado', 'ref', 'ogr')

    empty_project = len(project.mapLayers()) == 0
    root = project.layerTreeRoot()
    group = root.insertGroup(0, 'Tamaulipas')
    loaded = 0
    failed = []

    if points:
        g_points = group.addGroup('Puntos')
        for name, title, color in POINT_LAYERS:
            vl = QgsVectorLayer(f'{gpkg}|layername={name}', title, 'ogr')
            if not vl.isValid():
                failed.append(name)
                continue
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle', 'color': color, 'size': POINT_SIZE,
                'size_unit': 'MM', 'outline_style': 'no'})
            vl.setRenderer(QgsSingleSymbolRenderer(symbol))
            vl.setReadOnly(True)
            vl.setAttribution(WOF_ATTRIBUTION)
            project.addMapLayer(vl, False)
            g_points.addLayer(vl)
            loaded += 1

    if polygons or irrigation:
        g_polys = group.addGroup('Polígonos')
    if polygons:
        for name, title, color, width in POLYGON_LAYERS:
            vl = QgsVectorLayer(f'{gpkg}|layername={name}', title, 'ogr')
            if not vl.isValid():
                failed.append(name)
                continue
            symbol = QgsFillSymbol.createSimple({
                'style': 'no', 'outline_color': color,
                'outline_width': width, 'outline_width_unit': 'MM'})
            vl.setRenderer(QgsSingleSymbolRenderer(symbol))
            vl.setReadOnly(True)
            vl.setAttribution(WOF_ATTRIBUTION)
            if name == 'municipios':
                vl.setLabeling(municipality_labels())
                vl.setLabelsEnabled(True)
            project.addMapLayer(vl, False)
            g_polys.addLayer(vl)
            loaded += 1

    if irrigation:
        name, title, color, width = DR_LAYER
        vl = QgsVectorLayer(f'{gpkg}|layername={name}', title, 'ogr')
        if vl.isValid():
            vl.setRenderer(QgsSingleSymbolRenderer(
                irrigation_symbol(color, width)))
            vl.setReadOnly(True)
            vl.setAttribution(DR_ATTRIBUTION)
            project.addMapLayer(vl, False)
            g_polys.addLayer(vl)  # debajo de los demás polígonos
            loaded += 1
        else:
            failed.append(name)

    if relief:
        g_relief = group.addGroup('Relieve')
        dem_path = os.path.join(plugin_dir, 'data', DEM_FILE)
        for maker in (dem_hillshade_layer, dem_color_layer):  # sombreado arriba
            rl = maker(dem_path) if os.path.exists(dem_path) else None
            if rl is None:
                failed.append(DEM_FILE)
                continue
            if DEM_SOURCE:
                rl.setAttribution(DEM_SOURCE)
            project.addMapLayer(rl, False)
            g_relief.addLayer(rl)
            loaded += 1

    if basemap:
        bm = QgsRasterLayer(BASEMAP_URI, BASEMAP_NAME, 'wms')
        if bm.isValid():
            project.addMapLayer(bm, False)
            group.addLayer(bm)  # la última del grupo: queda al fondo
            loaded += 1
        else:
            failed.append(BASEMAP_NAME)

    if loaded == 0:
        root.removeChildNode(group)
        return 0, failed

    # SRC del proyecto: si estaba vacío, el de los datos (UTM 14N).
    if empty_project and ref.isValid():
        project.setCrs(ref.crs())

    # Encuadre al estado.
    if ref.isValid() and iface is not None:
        canvas = iface.mapCanvas()
        tr = QgsCoordinateTransform(
            ref.crs(), canvas.mapSettings().destinationCrs(), project)
        extent = tr.transformBoundingBox(ref.extent())
        extent.scale(1.05)
        canvas.setExtent(extent)
        canvas.refresh()

    return loaded, failed
