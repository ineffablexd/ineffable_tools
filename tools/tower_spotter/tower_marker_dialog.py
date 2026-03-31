"""
Tower Spotter - QGIS Plugin
Copyright (C) 2026 Vicky Sharma

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import math
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTextEdit, QComboBox, QMessageBox,
    QHBoxLayout, QSpinBox, QProgressBar,
    QColorDialog, QRadioButton, QButtonGroup,
    QApplication
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature,
    QgsGeometry, QgsField,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
    QgsMapLayer,
    QgsWkbTypes,
    QgsPointXY
)

from qgis.PyQt.QtCore import QVariant
import xml.etree.ElementTree as ET


class TowerMarkerDialog(QDialog):

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

        self.setWindowTitle("Tower Spotter")
        self.resize(520, 580)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Line Layer:"))

        self.layer_combo = QComboBox()
        self.populate_layers()
        layout.addWidget(self.layer_combo)

        self.file_button = QPushButton("Or Select KML File")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Radius (meters):"))
        self.radius_input = QSpinBox()
        self.radius_input.setRange(1, 5000)
        self.radius_input.setValue(10)
        r_layout.addWidget(self.radius_input)
        layout.addLayout(r_layout)

        s_layout = QHBoxLayout()
        s_layout.addWidget(QLabel("Polygon Sides:"))
        self.segment_input = QSpinBox()
        self.segment_input.setRange(3, 128)
        self.segment_input.setValue(16)
        s_layout.addWidget(self.segment_input)
        layout.addLayout(s_layout)

        self.selected_color = QColor(255, 0, 0)
        self.color_button = QPushButton("Select Tower Color")
        self.color_button.clicked.connect(self.choose_color)
        layout.addWidget(self.color_button)

        layout.addWidget(QLabel("Rendering Mode:"))

        self.fill_radio = QRadioButton("Solid Fill")
        self.outline_radio = QRadioButton("Outline Only")
        self.fill_radio.setChecked(True)

        group = QButtonGroup()
        group.addButton(self.fill_radio)
        group.addButton(self.outline_radio)

        layout.addWidget(self.fill_radio)
        layout.addWidget(self.outline_radio)

        self.run_button = QPushButton("Process")
        self.run_button.clicked.connect(self.process_layer)
        layout.addWidget(self.run_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.save_button = QPushButton("Save Output")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_output)
        layout.addWidget(self.save_button)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

        self.input_layer = None
        self.output_layer = None

    # -------------------------------------------------

    def log_message(self, msg):
        self.log.append(msg)

    def populate_layers(self):
        self.layer_combo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer and \
               layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.layer_combo.addItem(layer.name(), layer)

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color)
        if color.isValid():
            self.selected_color = color

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select KML File", "", "KML Files (*.kml)"
        )
        if file_path:
            layer = QgsVectorLayer(file_path, os.path.basename(file_path), "ogr")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.input_layer = layer
                self.log_message("Loaded KML file.")

    # -------------------------------------------------

    def get_utm_crs(self, layer):
        center = layer.extent().center()
        lon = center.x()
        lat = center.y()
        zone = int((lon + 180) / 6) + 1
        epsg = 32600 + zone if lat >= 0 else 32700 + zone
        return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")

    # -------------------------------------------------

    def create_polygon(self, x, y, radius, sides):
        pts = []
        step = 2 * math.pi / sides
        for i in range(sides):
            angle = i * step
            pts.append(QgsPointXY(
                x + radius * math.cos(angle),
                y + radius * math.sin(angle)
            ))
        pts.append(pts[0])
        return QgsGeometry.fromPolygonXY([pts])

    # -------------------------------------------------

    def process_layer(self):

        layer = self.input_layer or self.layer_combo.currentData()
        if not layer:
            QMessageBox.warning(self, "Error", "No input layer selected.")
            return

        radius = self.radius_input.value()
        sides = self.segment_input.value()

        utm = self.get_utm_crs(layer)
        forward = QgsCoordinateTransform(layer.crs(), utm, QgsProject.instance())
        reverse = QgsCoordinateTransform(utm, layer.crs(), QgsProject.instance())

        self.output_layer = QgsVectorLayer(
            f"Polygon?crs={layer.crs().authid()}",
            f"{layer.name()}_Towers",
            "memory"
        )

        provider = self.output_layer.dataProvider()
        provider.addAttributes([QgsField("Tower_ID", QVariant.Int)])
        self.output_layer.updateFields()

        tid = 1
        feats = []

        for f in layer.getFeatures():
            geom = f.geometry()
            geom.transform(forward)

            for pt in geom.vertices():
                poly = self.create_polygon(pt.x(), pt.y(), radius, sides)
                poly.transform(reverse)

                feat = QgsFeature()
                feat.setGeometry(poly)
                feat.setAttributes([tid])
                feats.append(feat)
                tid += 1

        provider.addFeatures(feats)
        QgsProject.instance().addMapLayer(self.output_layer)

        self.save_button.setEnabled(True)
        self.log_message("Processing complete.")

    # -------------------------------------------------
    # ⭐ PERFECT GOOGLE EARTH EXPORT
    # -------------------------------------------------

    def save_output(self):

        if not self.output_layer:
            return

        default_name = self.output_layer.name() + ".kml"

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Output", default_name, "KML Files (*.kml)"
        )

        if not path:
            return

        if not path.lower().endswith(".kml"):
            path += ".kml"

        # Force WGS84
        wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            self.output_layer.crs(), wgs84, QgsProject.instance()
        )

        color = self.selected_color

        # KML format: AABBGGRR
        # Proper KML color encoding (AABBGGRR)
        r = color.red()
        g = color.green()
        b = color.blue()

        kml_color = "{:02x}{:02x}{:02x}{:02x}".format(
            255,   # Alpha (fully opaque)
            b,
            g,
            r
        )
        
        kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        doc = ET.SubElement(kml, "Document")

        style = ET.SubElement(doc, "Style", id="towerStyle")
        poly_style = ET.SubElement(style, "PolyStyle")
        ET.SubElement(poly_style, "color").text = kml_color
        ET.SubElement(poly_style, "fill").text = "1" if self.fill_radio.isChecked() else "0"
        ET.SubElement(poly_style, "outline").text = "1"

        for f in self.output_layer.getFeatures():

            geom = f.geometry()
            geom.transform(transform)

            pm = ET.SubElement(doc, "Placemark")
            ET.SubElement(pm, "styleUrl").text = "#towerStyle"

            polygon = ET.SubElement(pm, "Polygon")
            outer = ET.SubElement(polygon, "outerBoundaryIs")
            ring = ET.SubElement(outer, "LinearRing")
            coords_elem = ET.SubElement(ring, "coordinates")

            coords = []
            for r in geom.asPolygon():
                for p in r:
                    coords.append(f"{p.x()},{p.y()},0")

            coords_elem.text = " ".join(coords)

        ET.ElementTree(kml).write(
            path,
            xml_declaration=True,
            encoding="UTF-8"
        )

        self.log_message(f"KML exported correctly for Google Earth: {path}")