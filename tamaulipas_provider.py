import os

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .tamaulipas_algorithm import LoadTamaulipasBaseAlgorithm


class TamaulipasBaseProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(LoadTamaulipasBaseAlgorithm())

    def id(self):
        return 'vaquerosgis'

    def name(self):
        return 'VaquerosGIS'

    def longName(self):
        return 'VaquerosGIS'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.png'))
