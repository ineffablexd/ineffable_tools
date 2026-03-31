# 🗺️ Auto Layout Generator

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/ineffablexd/auto_layout_generator)
[![License](https://img.shields.io/badge/license-GPL--2.0-green.svg)](LICENSE)
[![QGIS](https://img.shields.io/badge/QGIS-3.0+-orange.svg)](https://qgis.org)

An advanced cartographic layout automation tool for QGIS that streamlines the creation of professional map layouts. It simplifies complex workflows by automating the generation of dynamic grids, synchronized scale bars, and intelligent styling.

---

## 🖼️ Visual Workflow

<p align="center">
  <img src="assets/ui_screenshot.png" alt="Auto Layout Generator UI" width="45%">
  <img src="assets/output.png" alt="Map Output" width="45%">
</p>
<p align="center">
  <i>The Auto Layout Generator interface and a sample of the automated map output.</i>
</p>

---

## ✨ Key Features

- 🎯 **Dynamic Grids:** Automated WGS84 coordinate grid generation with precise label placement.
- 📏 **Adaptive Scaling:** Intelligently switches between meters and kilometers based on map extent.
- 🧩 **Synchronized Elements:** Real-time synchronization of scale bars, north arrows, and legends.
- 🎨 **Automated Styling:** Applies professional cartographic styles to layout components instantly.
- 🛠️ **User Interface:** A modern, intuitive dialog with progress tracking for long-running tasks.
- 🔄 **Coordinate Logic:** Handles complex transformations to ensure valid rendering across different map extents.

---

## 🚀 Installation

### Option 1: Via QGIS Plugin Manager (Recommended)

1. Open **QGIS**.
2. Go to **Plugins** > **Manage and Install Plugins...**
3. Search for **Auto Layout Generator**.
4. Click **Install Plugin**.

### Option 2: Manual Installation

1. Download the latest release as a ZIP file.
2. Extract the folder into your QGIS plugins directory:
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Windows:** `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS and enable the plugin in the Plugin Manager.

---

## 📖 How to Use

1.  **Prepare your map:** Load the required vector and raster layers into your QGIS project.
2.  **Launch the tool:** Navigate to the top-level **Ineffable Tools** menu and select **Auto Layout Generator**.
3.  **Configure settings:** Use the dialog tabs to set your grid spacing, scale bar preferences, and legend options.
4.  **Generate layout:** Click the **Generate** button to begin the automated layout creation.
5.  **Review & Export:** The tool will create a new print layout with all elements perfectly aligned and styled, ready for export.

---

## 👤 Author & License

- **Author:** Vicky Sharma
- **Email:** [vsharma@powergrid.in](mailto:vsharma@powergrid.in)
- **Repository:** [Ineffable Tools / Auto Layout Generator](https://github.com/ineffablexd/auto_layout_generator)
- **License:** Distributed under the **GPL-2.0-or-later** license. See `LICENSE` for more information.

<p align="center">
  Made with ❤️ by <a href="https://github.com/ineffablexd">Ineffable</a>
</p>
