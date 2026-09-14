import os

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
)

from .loader import load_tamaulipas_base

# Sin hilos: el algoritmo añade capas al proyecto y mueve el mapa, y eso
# solo se puede hacer desde el hilo principal de QGIS.
try:
    from qgis.core import Qgis
    NO_THREADING = Qgis.ProcessingAlgorithmFlag.NoThreading
except AttributeError:
    NO_THREADING = QgsProcessingAlgorithm.FlagNoThreading


class LoadTamaulipasBaseAlgorithm(QgsProcessingAlgorithm):

    BASEMAP = 'BASEMAP'
    POLYGONS = 'POLYGONS'
    POINTS = 'POINTS'
    IRRIGATION = 'IRRIGATION'
    RELIEF = 'RELIEF'

    def createInstance(self):
        return LoadTamaulipasBaseAlgorithm()

    def name(self):
        return 'load_tamaulipas_base'

    def displayName(self):
        return 'VaquerosGIS'

    def shortDescription(self):
        # Se ve al pasar el ratón sobre el algoritmo en la caja de herramientas.
        return 'Cartografía base de proyectos GIS en el estado de Tamaulipas'

    def group(self):
        return 'Cartografía base'

    def groupId(self):
        return 'base_maps'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.png'))

    def flags(self):
        return super().flags() | NO_THREADING

    def shortHelpString(self):
        logo = QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__), 'icon.png')).toString()
        return (
            '<p>Cartografía base de proyectos GIS en el estado de Tamaulipas</p>'
            '<table><tr>'
            f'<td valign="middle"><img src="{logo}" width="64" height="64"></td>'
            '<td valign="middle" style="padding-left:10px">'
            'Creado por Daniel Ibarra Marinas y Ana Mónica de Jhesú García (Vienna)<br>'
            '<span style="color:#2e8a3d"><b>Facultad de Ingeniería '
            'y Ciencias</b></span><br>'
            '<span style="color:#d97706"><b>Universidad Autónoma de '
            'Tamaulipas</b></span>'
            '</td></tr></table>'

            '<p>Prepara en un clic una <b>base cartográfica de Tamaulipas</b> '
            'para empezar a trabajar: capas de referencia ya recortadas con '
            'el límite del estado, con estilo y en el orden adecuado. '
            'Marca lo que quieras cargar y pulsa <b>Ejecutar</b>.</p>'

            '<p><b>Qué puede añadir</b> (grupo "Tamaulipas"):</p>'
            '<p><b>Puntos</b>, arriba: localidades (8.004), colonias (87) y '
            'campus (1), de 0,5 mm.</p>'
            '<p><b>Polígonos</b>, en medio y solo con contorno: el límite '
            'del estado, los 43 municipios con su nombre en cursiva y las '
            'áreas de 63 localidades.</p>'
            '<p><b>Distritos de riego</b>: los 7 de Tamaulipas (002 Mante, '
            '025 Bajo Río Bravo, 026 Bajo Río San Juan, 029 Xicoténcatl, 050 '
            'Acuña Falcón, 086 Soto la Marina y 092A Río Pánuco, Unidad '
            'Ánimas), en azul celeste con trama rayada, debajo de los demás '
            'polígonos. Traen usuarios, superficies y volúmenes de agua del '
            'año agrícola 2016-2017. Se cargan sin recortar: del 050 solo el '
            '65 % cae dentro del estado. El área del polígono no coincide con '
            'la superficie oficial (campo sup_tot): para superficies, usa los '
            'atributos.</p>'
            '<p><b>Relieve</b> (casilla desmarcada por defecto): modelo '
            'digital de elevaciones de unos 90 m, con tintas hipsométricas '
            'suaves y un sombreado multidireccional encima. Va sobre la '
            'imagen de satélite y la tapa dentro del estado: apaga una de '
            'las dos según lo que necesites.</p>'
            '<p><b>Imagen de satélite</b> de Google, al fondo.</p>'

            '<p>Las capas se cargan en <b>solo lectura</b>, para no '
            'modificar por error los datos del plugin. Si el proyecto está '
            'vacío, el SRC pasa a WGS 84 / UTM zona 14N (EPSG:32614), que '
            'cubre todo el estado, y el mapa se encuadra en Tamaulipas.</p>'

            '<p style="color:#6b6b6b"><b>Fuentes:</b> Who\'s On First '
            '(https://whosonfirst.org/docs/licenses/) y, para los distritos '
            'de riego, CONAGUA a través del servicio INFOTECA de SEMARNAT; '
            'algunas fuentes de Who\'s On First '
            'exigen atribución (por ejemplo, GeoNames y '
            'Quattroshapes, CC-BY). Imagen de fondo: Google, sujeta a sus '
            'condiciones de servicio.</p>'
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterBoolean(
            self.BASEMAP, 'Imagen de satélite (Google)', defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.RELIEF, 'Relieve: modelo digital de elevaciones (tapa la '
            'imagen de satélite)', defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.POLYGONS, 'Polígonos: estado, municipios y localidades (áreas)',
            defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.IRRIGATION, 'Distritos de riego (los 7 de Tamaulipas)',
            defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.POINTS, 'Puntos: localidades, colonias y campus',
            defaultValue=True))

    def processAlgorithm(self, parameters, context, feedback):
        from qgis.utils import iface
        basemap = self.parameterAsBoolean(parameters, self.BASEMAP, context)
        polygons = self.parameterAsBoolean(parameters, self.POLYGONS, context)
        points = self.parameterAsBoolean(parameters, self.POINTS, context)
        irrigation = self.parameterAsBoolean(parameters, self.IRRIGATION, context)
        relief = self.parameterAsBoolean(parameters, self.RELIEF, context)
        if not (basemap or polygons or points or irrigation or relief):
            raise QgsProcessingException(
                'No has marcado nada: elige al menos una de las opciones.')
        plugin_dir = os.path.dirname(__file__)
        loaded, failed = load_tamaulipas_base(
            iface, plugin_dir, basemap=basemap, polygons=polygons, points=points,
            irrigation=irrigation, relief=relief)
        if loaded == 0:
            raise QgsProcessingException(
                'No se pudieron cargar las capas de Tamaulipas.')
        if failed:
            feedback.pushWarning(f'No se pudo cargar: {", ".join(failed)}.')
        else:
            feedback.pushInfo('Base de Tamaulipas cargada.')
        return {}
