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

from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    QgsPalLayerSettings,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayerSimpleLabeling,
    QgsCoordinateTransform,
    QgsFillSymbol,
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
MUNI_LABEL_SIZE = 5
MUNI_LABEL_COLOR = MUNI_COLOR
MUNI_LABEL_BUFFER = '#000000'


def municipality_labels():
    """Etiquetas de los municipios: 5 pt, cursiva, del mismo color que el
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


def load_tamaulipas_base(iface, plugin_dir, basemap=True, polygons=True,
                         points=True):
    """Carga en el proyecto actual un grupo "Tamaulipas" con las partes
    elegidas: imagen de satélite, polígonos y puntos.

    Devuelve (cargadas, fallidas): número de capas añadidas y lista de las
    que no se pudieron cargar. Debe ejecutarse en el hilo principal de QGIS
    (toca el proyecto y el lienzo del mapa).
    """
    project = QgsProject.instance()
    gpkg = os.path.join(plugin_dir, 'data', 'tamaulipas_base.gpkg')
    if not os.path.exists(gpkg):
        return 0, ['tamaulipas_base.gpkg']
    if not (basemap or polygons or points):
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

    if polygons:
        g_polys = group.addGroup('Polígonos')
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
