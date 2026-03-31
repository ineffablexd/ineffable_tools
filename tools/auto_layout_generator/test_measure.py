import sys
sys.path.append("/usr/share/qgis/python")
from qgis.core import QgsApplication, QgsLayoutItemMap, QgsLayoutMeasurement, QgsProject, QgsPrintLayout, QgsUnitTypes

app = QgsApplication([], False)
app.initQgis()

project = QgsProject.instance()
layout = QgsPrintLayout(project)
map_item = QgsLayoutItemMap(layout)
try:
    map_item.setFrameStrokeWidth(1.2)
    print("Float worked")
except Exception as e:
    print("Float failed:", type(e), e)

try:
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(1.2))
    print("QgsLayoutMeasurement(1.2) worked")
except Exception as e:
    print("QgsLayoutMeasurement(1.2) failed:", type(e), e)

try:
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(1.2, QgsUnitTypes.LayoutMillimeters))
    print("QgsLayoutMeasurement(1.2, QgsUnitTypes.LayoutMillimeters) worked")
except Exception as e:
    print("QgsLayoutMeasurement(1.2, QgsUnitTypes.LayoutMillimeters) failed:", type(e), e)

app.exitQgis()
