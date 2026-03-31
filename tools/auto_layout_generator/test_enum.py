import sys
sys.path.append("/usr/share/qgis/python")
from qgis.core import QgsApplication, QgsLayoutItemMapGrid

app = QgsApplication([], False)
app.initQgis()

print("QGIS INIT SUCCESS")
for k in dir(QgsLayoutItemMapGrid):
    if "Format" in k or "Decimal" in k:
        print("F:", k)
for k in dir(QgsLayoutItemMapGrid):
    if "Position" in k or "Outside" in k or "Inside" in k:
        print("P:", k)
app.exitQgis()
