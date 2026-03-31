# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QAction, QMessageBox, QDialog, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QKeySequenceEdit, QListWidget,
    QListWidgetItem, QProgressBar
)
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QIcon, QKeySequence
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsProcessingFeedback
from qgis.gui import QgsProjectionSelectionWidget
import processing
import os

STYLE = """
QDialog {
    background-color: #f8f9fa;
    border-radius: 10px;
}
QLabel {
    color: #2d3436;
    font-weight: 500;
}
QPushButton {
    background-color: #0984e3;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    min-width: 120px;
}
QPushButton:hover {
    background-color: #74b9ff;
}
QPushButton#delete_btn {
    background-color: #d63031;
}
QPushButton#delete_btn:hover {
    background-color: #ff7675;
}
QListWidget {
    background-color: white;
    border: 1px solid #dfe6e9;
    border-radius: 8px;
    padding: 5px;
    font-size: 13px;
    color: #2d3436;
    outline: none;
}
QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #f1f2f6;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #e3f2fd;
    color: #0984e3;
    font-weight: bold;
}
QKeySequenceEdit {
    background-color: white;
    border: 1px solid #dfe6e9;
    border-radius: 6px;
    padding: 8px;
}
"""

MAX_SHORTCUTS = 9

class QuickReprojectPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.settings = QSettings()
        self.shortcuts = self.load_shortcuts()
        self.menu_name = "Ineffable Tools"
        self.menu = None
        self.plugin_menu = None
        
        plugin_dir = os.path.dirname(__file__)
        self.icon = QIcon(os.path.join(plugin_dir, "icon.png"))

    def initGui(self):
        self.menu = None
        for action in self.iface.mainWindow().menuBar().actions():
            if action.text() == self.menu_name:
                self.menu = action.menu()
                break
        
        if not self.menu:
             self.menu = self.iface.mainWindow().menuBar().addMenu(self.menu_name)

        self.plugin_menu = self.menu.addMenu(self.icon, "Quick Reproject")
        
        self.create_actions()
        self.add_manager()

    def unload(self):
        for a in self.actions:
            self.plugin_menu.removeAction(a)
        
        if self.menu:
            self.menu.removeAction(self.plugin_menu.menuAction())

    def load_shortcuts(self):
        defaults = {
            "42N": ["EPSG:32642", "Alt+2"],
            "43N": ["EPSG:32643", "Alt+3"],
            "44N": ["EPSG:32644", "Alt+4"],
            "45N": ["EPSG:32645", "Alt+5"],
            "46N": ["EPSG:32646", "Alt+6"],
            "WGS84": ["EPSG:4326", "Alt+8"]
        }
        loaded = self.settings.value("quick_reproject/shortcuts", defaults)
        
        # In case the user previously deleted 44N or WGS84, let's restore any missing defaults
        if isinstance(loaded, dict):
            for k, v in defaults.items():
                if k not in loaded:
                    loaded[k] = v
                    
            # save the corrected back to settings
            self.settings.setValue("quick_reproject/shortcuts", loaded)
            return loaded
            
        return defaults

    def save_shortcuts(self):
        self.settings.setValue("quick_reproject/shortcuts", self.shortcuts)

    def create_actions(self):
        for name, (crs, shortcut) in self.shortcuts.items():
            act = QAction(self.icon, f"Reproject to {name}", self.iface.mainWindow())
            clean_shortcut = shortcut.replace("Ctrl", "Alt")
            act.setShortcut(QKeySequence(clean_shortcut))
            act.triggered.connect(lambda _, c=crs, n=name: self.reproject(c, n))
            self.plugin_menu.addAction(act)
            self.actions.append(act)

    def add_manager(self):
        self.plugin_menu.addSeparator()
        act = QAction(QIcon(), "⚙ Manage Reprojection Shortcuts", self.iface.mainWindow())
        act.triggered.connect(self.open_manager)
        self.plugin_menu.addAction(act)
        self.actions.append(act)

    def open_manager(self):
        dlg = ManagerDialog(self)
        dlg.exec_()

    def get_layers(self):
        return self.iface.layerTreeView().selectedLayers()

    def reproject(self, crs_authid, suffix):
        layers = self.get_layers()
        if not layers:
            self.iface.messageBar().pushMessage("Quick Reproject", "No layers selected.", level=1, duration=3)
            return

        target = QgsCoordinateReferenceSystem(crs_authid)

        progress = QProgressBar()
        progress.setMaximum(len(layers))
        progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        msg = self.iface.messageBar().createMessage("🔄 Reprojecting layers...")
        msg.layout().addWidget(progress)
        self.iface.messageBar().pushWidget(msg, level=0)

        feedback = QgsProcessingFeedback()
        
        for i, layer in enumerate(layers):
            if layer.crs() == target:
                progress.setValue(i + 1)
                continue

            name = layer.name() + "_" + suffix

            if layer.type() == 0:
                res = processing.run("native:reprojectlayer", {
                    'INPUT': layer,
                    'TARGET_CRS': target,
                    'OUTPUT': 'memory:'
                }, feedback=feedback)
                new_layer = res['OUTPUT']
            else:
                res = processing.run("gdal:warpreproject", {
                    'INPUT': layer.source(),
                    'TARGET_CRS': crs_authid,
                    'RESAMPLING': 0,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }, feedback=feedback)
                from qgis.core import QgsRasterLayer
                new_layer = QgsRasterLayer(res['OUTPUT'], name)

            new_layer.setName(name)
            QgsProject.instance().removeMapLayer(layer.id())
            QgsProject.instance().addMapLayer(new_layer)
            progress.setValue(i + 1)

        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("✅ Done", f"Reprojected to {suffix}", level=0, duration=3)


class ManagerDialog(QDialog):

    def __init__(self, plugin):
        super().__init__(plugin.iface.mainWindow())
        self.plugin = plugin
        self.setWindowTitle("Quick Reproject Manager")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        header = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(self.plugin.icon.pixmap(32, 32))
        title = QLabel("Reprojection Settings")
        title.setStyleSheet("font-size:20px; font-weight:bold; color: #0984e3;")
        header.addWidget(title_icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        instruction = QLabel("Select layers in QGIS and use hotkeys to transform them instantly.")
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #636e72; font-style: italic; margin-bottom: 5px;")
        layout.addWidget(instruction)

        self.list_widget = QListWidget()
        self.refresh_list()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        add_btn = QPushButton("+ Add Shortcut")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_dialog)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("delete_btn")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_selected)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def refresh_list(self):
        self.list_widget.clear()
        for key, (crs, shortcut) in self.plugin.shortcuts.items():
            item = QListWidgetItem(f"{key} → {shortcut.replace('Ctrl', 'Alt')}")
            item.setData(1, key)
            self.list_widget.addItem(item)

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item: return

        key = item.data(1)
        del self.plugin.shortcuts[key]
        self.plugin.save_shortcuts()
        self.refresh_list()

    def open_add_dialog(self):
        dlg = AddDialog(self.plugin)
        dlg.exec_()
        self.refresh_list()


class AddDialog(QDialog):

    def __init__(self, plugin):
        super().__init__(plugin.iface.mainWindow())
        self.plugin = plugin
        self.setWindowTitle("Create New Shortcut")
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        title = QLabel("New Transformation")
        title.setStyleSheet("font-size:18px; font-weight:bold; color: #0984e3;")
        layout.addWidget(title)

        layout.addWidget(QLabel("1. Targeted Coordinate System (CRS)"))
        self.crs_widget = QgsProjectionSelectionWidget()
        layout.addWidget(self.crs_widget)

        layout.addWidget(QLabel("2. Assign Hotkey"))
        self.key_edit = QKeySequenceEdit()
        layout.addWidget(self.key_edit)

        save_btn = QPushButton("Save Shortcut")
        save_btn.setFixedHeight(45)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        if len(self.plugin.shortcuts) >= MAX_SHORTCUTS:
            QMessageBox.warning(self, "Limit", "Max 9 shortcuts allowed")
            return

        crs = self.crs_widget.crs().authid()
        key = self.key_edit.keySequence().toString().replace("Ctrl", "Alt")
        suffix = crs.split(":")[1]

        self.plugin.shortcuts[suffix] = [crs, key]
        self.plugin.save_shortcuts()
        self.close()


def classFactory(iface):
    return QuickReprojectPlugin(iface)