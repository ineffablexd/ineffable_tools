
from qgis.PyQt.QtCore import QSettings, QVariant
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QComboBox, QMenu
from qgis.core import (QgsProject, QgsMapLayer, QgsWkbTypes, QgsVectorLayer, QgsField, QgsCoordinateTransform, 
                       QgsSpatialIndex, QgsGeometry, QgsFeature, QgsMessageLog, Qgis, QgsMarkerSymbol,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsPalLayerSettings, QgsTextFormat,
                       QgsTextBufferSettings, QgsVectorLayerSimpleLabeling, QgsProperty, QgsPointXY)
import math
import os
from qgis.PyQt.QtGui import QColor, QIcon

class CrossingAngelAnalyser:

    def __init__(self, iface):
        self.iface = iface
        self.menu_name = "Ineffable Tools"
        self.route_id = None
        self.obstacle_ids = []
        self.layer_id = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.icon = QIcon(icon_path)
        self.action = QAction(self.icon, "Crossing Angel Analyser", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        
        menu_bar = self.iface.mainWindow().menuBar()
        self.ineffable_menu = None
        for action in menu_bar.actions():
            if action.text() == self.menu_name:
                self.ineffable_menu = action.menu()
                break
        
        if not self.ineffable_menu:
            self.ineffable_menu = menu_bar.addMenu(self.menu_name)
            
        self.ineffable_menu.addAction(self.action)

    def unload(self):
        if hasattr(self, 'ineffable_menu') and self.ineffable_menu:
            self.ineffable_menu.removeAction(self.action)

    def run(self):
        self.widget = QWidget()
        layout = QVBoxLayout()

        self.route_combo = QComboBox()
        self.obstacle_list = QListWidget()
        self.obstacle_list.setSelectionMode(QListWidget.MultiSelection)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.route_combo.addItem(layer.name(), layer.id())
                self.obstacle_list.addItem(layer.name())

        self.btn = QPushButton("Enable Live Angles")
        self.btn.setCheckable(True)
        self.btn.clicked.connect(self.toggle_live)

        layout.addWidget(QLabel("Input Layer"))
        layout.addWidget(self.route_combo)
        layout.addWidget(QLabel("Crossing Layers"))
        layout.addWidget(self.obstacle_list)
        layout.addWidget(self.btn)

        self.widget.setLayout(layout)
        self.dock = QDockWidget("Crossing Angel Analyser", self.iface.mainWindow())
        self.dock.setWidget(self.widget)
        self.dock.setFloating(True) 
        self.iface.addDockWidget(2, self.dock)

    def toggle_live(self):
        if self.btn.isChecked():
            self.btn.setText("Analyser Running... (Click to Stop)")
            self.btn.setStyleSheet("background-color: #007832; color: white; border-radius: 5px; padding: 5px;")
            self.start_live()
        else:
            self.btn.setText("Enable Live Angles")
            self.btn.setStyleSheet("")
            self.stop_live()

    def stop_live(self):
        project = QgsProject.instance()
        if self.route_id:
            route = project.mapLayer(self.route_id)
            if route:
                try:
                    route.geometryChanged.disconnect(self.update)
                    route.featureAdded.disconnect(self.update)
                    route.featureDeleted.disconnect(self.update)
                except: pass
        
        for lyr in project.mapLayersByName("Angles"):
            project.removeMapLayer(lyr.id())
        
        self.route_id = None
        self.layer_id = None

    def start_live(self):
        try:
            self.route_id = self.route_combo.currentData()
            self.obstacle_ids = []
            project = QgsProject.instance()
            for item in self.obstacle_list.selectedItems():
                layers = project.mapLayersByName(item.text())
                if layers: self.obstacle_ids.append(layers[0].id())

            route = project.mapLayer(self.route_id)
            if route:
                try: route.geometryChanged.disconnect(self.update)
                except: pass
                route.geometryChanged.connect(self.update)
                route.featureAdded.connect(self.update)
                route.featureDeleted.connect(self.update)
                QgsMessageLog.logMessage("Live Analysis Connection Established", "CrossingAngel", Qgis.Info)
                self.update()
        except Exception as e:
            QgsMessageLog.logMessage(f"Start Live Error: {str(e)}", "CrossingAngel", Qgis.Critical)

    def update(self):
        try:
            project = QgsProject.instance()
            route = project.mapLayer(self.route_id)
            if not route: return

            target_crs = project.crs()
            
            angles_layer = None
            if self.layer_id:
                angles_layer = project.mapLayer(self.layer_id)
            
            if not angles_layer:
                existing = project.mapLayersByName("Angles")
                if existing:
                    angles_layer = existing[0]
                    self.layer_id = angles_layer.id()
                else:
                    angles_layer = QgsVectorLayer("Point?crs=" + target_crs.authid(), "Angles", "memory")
                    project.addMapLayer(angles_layer)
                    self.layer_id = angles_layer.id()
                    
                    pr = angles_layer.dataProvider()
                    pr.addAttributes([QgsField("angle", QVariant.Double), QgsField("a1", QVariant.Double), QgsField("a2", QVariant.Double)])
                    angles_layer.updateFields()

                    root = project.layerTreeRoot()
                    node = root.findLayer(angles_layer.id())
                    if node:
                        new_node = node.clone()
                        root.insertChildNode(0, new_node)
                        root.removeChildNode(node)
                    self.style(angles_layer)

            feats = []
            xform_route = QgsCoordinateTransform(route.crs(), target_crs, project)
            g1_list = []
            for f in route.getFeatures():
                if f.hasGeometry():
                    g = QgsGeometry(f.geometry())
                    g.transform(xform_route)
                    g1_list.append(g)

            for obs_id in self.obstacle_ids:
                obs = project.mapLayer(obs_id)
                if not obs: continue
                
                xform_obs = QgsCoordinateTransform(obs.crs(), target_crs, project)
                obs_geoms = []
                for f in obs.getFeatures():
                    if f.hasGeometry():
                        g = QgsGeometry(f.geometry())
                        g.transform(xform_obs)
                        obs_geoms.append(g)

                index = QgsSpatialIndex()
                for i, g in enumerate(obs_geoms): index.addFeature(i, g.boundingBox())

                for g1 in g1_list:
                    for idx in index.intersects(g1.boundingBox()):
                        g2 = obs_geoms[idx]
                        if g1.intersects(g2):
                            inter = g1.intersection(g2)
                            if inter.isEmpty(): continue
                            
                            def get_pts(geom):
                                p_list = []
                                if geom.type() == QgsWkbTypes.PointGeometry:
                                    if geom.isMultipart():
                                        for p in geom.asMultiPoint(): p_list.append(QgsPointXY(p))
                                    else:
                                        p_list.append(QgsPointXY(geom.asPoint()))
                                elif geom.isMultipart() or geom.type() == QgsWkbTypes.LineGeometry or geom.type() == QgsWkbTypes.PolygonGeometry:
                                    try:
                                        # Handle Geometry Collections and other types
                                        for i in range(geom.constGet().partCount()):
                                            part = QgsGeometry(geom.constGet().partAt(i).clone())
                                            p_list.extend(get_pts(part))
                                    except: pass
                                return p_list

                            for pt in get_pts(inter):
                                try:
                                    v1 = self.vec(g1, pt)
                                    v2 = self.vec(g2, pt)
                                    ang = self.angle(v1, v2)
                                    if ang > 90: ang = 180 - ang
                                    
                                    f = QgsFeature(angles_layer.fields())
                                    f.setGeometry(QgsGeometry.fromPointXY(pt))
                                    f.setAttributes([round(ang, 2), 0, 0])
                                    feats.append(f)
                                except: continue

            angles_layer.startEditing()
            angles_layer.dataProvider().truncate()
            angles_layer.addFeatures(feats)
            angles_layer.commitChanges()
            angles_layer.triggerRepaint()
            QgsMessageLog.logMessage(f"Crossing Analysis: Found {len(feats)} intersections.", "CrossingAngel", Qgis.Info)
            
        except Exception as e:
            import traceback
            QgsMessageLog.logMessage(f"Update Error: {str(e)}\n{traceback.format_exc()}", "CrossingAngel", Qgis.Critical)

    def vec(self, geom, pt):
        res = geom.closestSegmentWithContext(pt)
        next_v_idx = res[2]
        p1 = geom.vertexAt(next_v_idx - 1)
        p2 = geom.vertexAt(next_v_idx)
        return (p2.x() - p1.x(), p2.y() - p1.y())

    def angle(self, v1, v2):
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        if mag1 == 0 or mag2 == 0: return 0
        cos_theta = max(-1, min(1, dot/(mag1*mag2)))
        return math.degrees(math.acos(cos_theta))

    def style(self, layer):
        red, blue, green = '#9E1303', '#00558E', '#057F38'
        categories = []
        def make_symbol(color):
            return QgsMarkerSymbol.createSimple({'color': color, 'size': '1.6', 'outline_color': 'transparent'})

        categories.append(QgsRendererCategory(red, make_symbol(red), '<70°'))
        categories.append(QgsRendererCategory(blue, make_symbol(blue), '70-80°'))
        categories.append(QgsRendererCategory(green, make_symbol(green), '80-90°'))

        expr = f"CASE WHEN angle < 70 THEN '{red}' WHEN angle < 80 THEN '{blue}' ELSE '{green}' END"
        layer.setRenderer(QgsCategorizedSymbolRenderer(expr, categories))

        settings = QgsPalLayerSettings()
        settings.fieldName = "round(angle,1) || '°'"
        settings.enabled = True
        settings.isExpression = True
        settings.placement = QgsPalLayerSettings.AroundPoint
        settings.dist = 3.5

        text_format = QgsTextFormat()
        text_format.setSize(13)
        text_format.setNamedStyle("Bold")
        settings.dataDefinedProperties().setProperty(QgsPalLayerSettings.Color, QgsProperty.fromExpression(expr))

        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(1.0)
        buffer.setColor(QColor("white"))
        text_format.setBuffer(buffer)
        
        settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()
