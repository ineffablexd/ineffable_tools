import os
import xml.etree.ElementTree as ET
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon, QKeySequence
from qgis.core import QgsApplication, QgsSettings
from qgis.gui import QgsGui

class IneffableToolsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugins = []
        
    def initGui(self):
        # 1. Load all 7 sub-plugins
        tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        if os.path.isdir(tools_dir):
            for tool_folder in os.listdir(tools_dir):
                tool_path = os.path.join(tools_dir, tool_folder)
                if os.path.isdir(tool_path) and not tool_folder.startswith('__'):
                    try:
                        import importlib
                        module_name = f"ineffable_tools_plugin.tools.{tool_folder}"
                        module = importlib.import_module(module_name)
                        if hasattr(module, 'classFactory'):
                            plugin_instance = module.classFactory(self.iface)
                            self.plugins.append(plugin_instance)
                            # Let the individual plugin register itself in the UI
                            plugin_instance.initGui()
                    except Exception as e:
                        self.iface.messageBar().pushMessage("Ineffable Tools error", f"Failed to load {tool_folder}: {str(e)}", level=2)
                        
        # 2. Apply shortcuts to the registered actions & QGIS globally
        self.apply_shortcuts()

    def unload(self):
        # Unload all sub-plugins
        for plugin in self.plugins:
            try:
                plugin.unload()
            except Exception as e:
                pass
        self.plugins.clear()

    def apply_shortcuts(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'shortcuts.xml')
        if not os.path.exists(xml_path):
            return
            
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            settings = QgsSettings()
            main_window = self.iface.mainWindow()
            all_actions = main_window.findChildren(QAction)
            
            manager = QgsGui.shortcutsManager()
            
            for action_elem in root.findall('action'):
                name = action_elem.get('name')
                shortcut = action_elem.get('shortcut')
                setting_key = action_elem.get('setting')
                
                if name and setting_key:
                    # Save to QgsSettings so it persists across sessions
                    settings.setValue(setting_key, shortcut)
                    
                    # Update active loaded actions matching the name/objectName
                    clean_name = name.replace('&', '')
                    for action in all_actions:
                        if action.text().replace('&', '') == clean_name or action.objectName() == name:
                            action.setShortcut(QKeySequence(shortcut))
                            try:
                                manager.registerAction(action, shortcut)
                            except Exception:
                                pass

        except Exception as e:
            self.iface.messageBar().pushMessage("Ineffable Tools warning", f"Error applying shortcuts: {str(e)}", level=1)
