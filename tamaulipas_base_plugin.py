"""
VaquerosGIS: botón, menú y proveedor de Processing.
La carga de capas está en loader.py.
"""
import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis, QgsApplication

from .tamaulipas_provider import TamaulipasBaseProvider

try:
    from qgis.PyQt import sip
except ImportError:  # instalaciones antiguas
    import sip


class TamaulipasBasePlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.provider = None
        self.menu = 'VaquerosGIS'

    def initProcessing(self):
        provider = TamaulipasBaseProvider()
        if QgsApplication.processingRegistry().addProvider(provider):
            self.provider = provider
        else:
            self.provider = None

    def initGui(self):
        self.initProcessing()
        icon = QIcon(os.path.join(self.plugin_dir, 'icon.png'))
        self.action = QAction(icon, 'VaquerosGIS', self.iface.mainWindow())
        self.action.setToolTip('VaquerosGIS: cartografía base de proyectos GIS en el estado de Tamaulipas')
        self.action.setStatusTip('Cartografía base de proyectos GIS en el estado de Tamaulipas')
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        if self.action is not None:
            self.iface.removePluginMenu(self.menu, self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None
        if self.provider is not None and not sip.isdeleted(self.provider):
            QgsApplication.processingRegistry().removeProvider(self.provider)
        self.provider = None

    def run(self):
        """Abre la ventana del algoritmo, con las casillas para elegir qué
        se carga."""
        import processing
        try:
            processing.execAlgorithmDialog(
                'vaquerosgis:load_tamaulipas_base', {})
        except Exception as e:  # por ejemplo, si el proveedor no se registró
            self.iface.messageBar().pushMessage(
                'VaquerosGIS',
                f'No se pudo abrir la ventana del algoritmo: {e}',
                level=Qgis.Critical, duration=10)
