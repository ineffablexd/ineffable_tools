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
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from .tower_marker_dialog import TowerMarkerDialog

class TowerMarkerPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.toolbar = None
        self.menu_name = "Ineffable Tools"

    def initGui(self):
        # 1. Setup icon and action
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(
            QIcon(icon_path), 
            "Tower Spotter", 
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        # 2. Add to toolbar
        self.toolbar = self.iface.addToolBar(self.menu_name)
        self.toolbar.setObjectName("IneffableTools")
        self.toolbar.addAction(self.action)

        # 3. Add to "Ineffable Tools" menu
        main_menu = self.iface.mainWindow().menuBar()
        found_menu = None
        
        # Find existing "Ineffable Tools" menu
        for action in main_menu.actions():
            if action.text() == self.menu_name:
                found_menu = action.menu()
                break
        
        # Create it if it doesn't exist
        if not found_menu:
            found_menu = QMenu(self.menu_name, self.iface.mainWindow())
            main_menu.addMenu(found_menu)
            
        found_menu.addAction(self.action)

    def unload(self):
        # 1. Remove action from menu
        main_menu = self.iface.mainWindow().menuBar()
        for action in main_menu.actions():
            if action.text() == self.menu_name:
                menu = action.menu()
                if menu:
                    menu.removeAction(self.action)
                break

        # 2. Remove toolbar
        if self.toolbar:
            self.iface.mainWindow().removeToolBar(self.toolbar)

    def run(self):
        dlg = TowerMarkerDialog(self.iface)
        dlg.exec_()