from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QProgressBar
from qgis.PyQt.QtCore import Qt
from qgis.core import *
from qgis.PyQt.QtGui import QFont

class LayoutDialog(QDialog):

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

        self.setWindowTitle("Auto Layout Generator")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Layout Name"))
        self.layout_name = QLineEdit("Styled Layout")
        layout.addWidget(self.layout_name)

        layout.addWidget(QLabel("Map Title"))
        self.title = QLineEdit("Map Title")
        layout.addWidget(self.title)

        layout.addWidget(QLabel("Author Name"))
        self.author = QLineEdit("Author")
        layout.addWidget(self.author)

        layout.addWidget(QLabel("Legend Layers"))
        self.layers = QListWidget()
        self.layers.setSelectionMode(self.layers.MultiSelection)

        for layer in QgsProject.instance().mapLayers().values():
            self.layers.addItem(layer.name())

        layout.addWidget(self.layers)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        btn = QPushButton("Generate Layout")
        btn.clicked.connect(self.generate_layout)
        layout.addWidget(btn)

        self.setLayout(layout)

    def generate_layout(self):
        self.progress_bar.setValue(0)

        project = QgsProject.instance()

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        base_name = self.layout_name.text()
        layout_name = base_name
        existing_layouts = [l.name() for l in project.layoutManager().printLayouts()]
        i = 1
        while layout_name in existing_layouts:
            layout_name = f"{base_name} {i}"
            i += 1
            
        layout.setName(layout_name)

        project.layoutManager().addLayout(layout)

        self.progress_bar.setValue(20)

        page = layout.pageCollection().pages()[0]
        page.setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)

        # PAGE BORDER
        border = QgsLayoutItemShape(layout)
        border.setShapeType(QgsLayoutItemShape.Rectangle)

        symbol = QgsFillSymbol.createSimple({
            'outline_color': 'black',
            'outline_width': '1.5',
            'color': '255,255,255,0'
        })

        border.setSymbol(symbol)
        layout.addLayoutItem(border)
        border.attemptMove(QgsLayoutPoint(5,5))
        border.attemptResize(QgsLayoutSize(287,200))

        # TITLE
        title = QgsLayoutItemLabel(layout)
        title.setText(self.title.text().upper())
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setHAlign(Qt.AlignHCenter)
        title.setVAlign(Qt.AlignVCenter)
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(5, 8))
        title.attemptResize(QgsLayoutSize(287, 20))
        
        self.progress_bar.setValue(40)

        # MAP
        canvas = self.iface.mapCanvas()
        
        map_item = QgsLayoutItemMap(layout)
        # 1. Set CRS first to avoid transformation errors (Match canvas CRS)
        map_item.setCrs(canvas.mapSettings().destinationCrs())
        
        # 2. Add to layout before setting geometry
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(15, 30))
        map_item.attemptResize(QgsLayoutSize(170, 160))
        
        # 3. Synchronize with canvas (This is the programmatic equivalent of the button in your screenshot)
        map_item.zoomToExtent(canvas.extent())
        
        # 4. Final check and refresh
        map_item.setFrameEnabled(True)
        try:
            map_item.setFrameStrokeWidth(QgsLayoutMeasurement(2.0))
        except TypeError:
            map_item.setFrameStrokeWidth(2.0)

        # Force render
        map_item.refresh()
        layout.refresh()

        # Update grid extent variable for the next section
        extent = map_item.extent()


        # GRID
        grid = QgsLayoutItemMapGrid("grid", map_item)
        grid.setEnabled(True)
        
        try:
            crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
            grid.setCrs(crs_dest)
            transform = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(), crs_dest, project)
            extent_4326 = transform.transformBoundingBox(extent)
            dx = extent_4326.width()
            dy = extent_4326.height()
            if dx > 0 and dy > 0:
                grid.setIntervalX(dx / 4.0)
                grid.setIntervalY(dy / 4.0)
            else:
                grid.setIntervalX(1)
                grid.setIntervalY(1)
        except Exception:
            dx = extent.width()
            dy = extent.height()
            if dx > 0 and dy > 0:
                grid.setIntervalX(dx / 4.0)
                grid.setIntervalY(dy / 4.0)
            else:
                grid.setIntervalX(1)
                grid.setIntervalY(1)
            
        grid.setAnnotationEnabled(True)
        try:
            grid.setAnnotationFormat(QgsLayoutItemMapGrid.DecimalWithSuffix)
        except AttributeError:
            pass
            
        try:
            # Positions outside frame
            grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Left)
            grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Right)
            grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Top)
            grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
            
            # Vertical annotations for left/right
            grid.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Left)
            grid.setAnnotationDirection(QgsLayoutItemMapGrid.Vertical, QgsLayoutItemMapGrid.Right)
            
            # Horizontal annotations for top/bottom
            grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Top)
            grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)
        except AttributeError:
            pass

        grid.setAnnotationFont(QFont("Arial", 8, QFont.Bold))
        map_item.grids().addGrid(grid)
        
        self.progress_bar.setValue(60)

        # NORTH ARROW
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")

        layout.addLayoutItem(north)
        north.attemptMove(QgsLayoutPoint(210, 30))
        north.attemptResize(QgsLayoutSize(20, 20))

        # NORTH LABEL
        north_label = QgsLayoutItemLabel(layout)
        north_label.setText("North")
        north_label.setFont(QFont("Arial", 12, QFont.Bold))
        north_label.setHAlign(Qt.AlignHCenter)
        layout.addLayoutItem(north_label)
        north_label.attemptMove(QgsLayoutPoint(210, 52))
        north_label.attemptResize(QgsLayoutSize(20, 10))

        # LEGEND
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        legend.setLinkedMap(map_item)
        legend.setFrameEnabled(True)
        try:
            legend.setFrameStrokeWidth(QgsLayoutMeasurement(1.0))
        except TypeError:
            legend.setFrameStrokeWidth(1.0)
        legend.setBackgroundEnabled(True)

        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(200, 100))
        
        self.progress_bar.setValue(80)

        # NORTH ARROW
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(":/images/north_arrows/layout_default_north_arrow.svg")

        layout.addLayoutItem(north)
        north.attemptMove(QgsLayoutPoint(210, 30))
        north.attemptResize(QgsLayoutSize(20, 20))

        # SCALEBAR
        scalebar = QgsLayoutItemScaleBar(layout)
        scalebar.setLinkedMap(map_item)
        
        # Dynamic units: km if scale is large, meters if scale is small
        current_scale = map_item.scale()
        if current_scale > 800: # Threshold for using km
            scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
        else:
            scalebar.setUnits(QgsUnitTypes.DistanceMeters)
            
        scalebar.setStyle('Single Box')
        layout.addLayoutItem(scalebar)
        scalebar.applyDefaultSize()
        scalebar.attemptMove(QgsLayoutPoint(200, 165))
        scalebar.update()

        # SCALE RATIO TEXT
        scale_label = QgsLayoutItemLabel(layout)
        scale_label.setText(f"Scale is : 1 : {int(current_scale)}")
        scale_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addLayoutItem(scale_label)
        scale_label.attemptMove(QgsLayoutPoint(200, 185))
        scale_label.attemptResize(QgsLayoutSize(80, 10))

        # CREATIVE DETAILS (Project info)
        from datetime import datetime
        metadata = QgsLayoutItemLabel(layout)
        crs_name = canvas.mapSettings().destinationCrs().authid()
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        metadata.setText(f"Projection: {crs_name}\nCreated: {time_str}")
        metadata.setFont(QFont("Arial", 7, QFont.StyleItalic))
        layout.addLayoutItem(metadata)
        metadata.attemptMove(QgsLayoutPoint(230, 195))
        metadata.attemptResize(QgsLayoutSize(55, 10))

        # AUTHOR
        author = QgsLayoutItemLabel(layout)
        author.setText("Author: " + self.author.text())
        layout.addLayoutItem(author)
        author.attemptMove(QgsLayoutPoint(20, 195))
        author.attemptResize(QgsLayoutSize(100, 15))


        self.progress_bar.setValue(100)
