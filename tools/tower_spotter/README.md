# Tower Spotter 🗼

<p align="center">
  <strong>Part of the <a href="https://github.com/ineffablexd">Ineffable Tools</a> Suite</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.3.3-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-GPL--2.0--or--later-green.svg" alt="License">
  <img src="https://img.shields.io/badge/QGIS-3.0+-orange.svg" alt="QGIS Compatibility">
</p>

---

## 📝 Description

**Tower Spotter** is a high-performance QGIS plugin tailored for electrical transmission line design and infrastructure planning. It automates the generation of precise tower footprint polygons at every vertex of your routing paths, ensuring engineering-grade accuracy through dynamic UTM reprojection and customizable geometry parameters.

---

## 🔄 Visual Workflow

### QGIS Integration (Before & After)

<p align="center">
  <img src="assets/before_qgis.jpg" width="45%" alt="QGIS Before">
  <img src="assets/after_qgis.jpg" width="45%" alt="QGIS After">
</p>

### Google Earth Export (Before & After)

<p align="center">
  <img src="assets/before_ge.jpg" width="45%" alt="Google Earth Before">
  <img src="assets/after_ge.jpg" width="45%" alt="Google Earth After">
</p>

### User Interface

<p align="center">
  <img src="assets/ui.png" width="60%" alt="Tower Spotter UI">
</p>

---

## ✨ Key Features

- 🗺️ **Dynamic UTM Reprojection**: Automatically calculates and applies the correct UTM zone based on your data's location for millisecond-accurate meter-based radius calculations.
- ⚡ **Automated Spotting**: Instantly generates tower footprints at every vertex of selected LineString layers or imported KML files.
- 🛠️ **Customizable Geometry**: Fine-tune your tower designs with adjustable **Radius (meters)** and **Polygon Sides** (from triangles to high-resolution circles).
- 🌍 **KML Ready**: Seamlessly export your generated towers into Google Earth compatible KML format (WGS84) with preserved styling.
- 🎨 **Flexible Rendering**: Choose between **Solid Fill** or **Outline Only** modes and pick any custom color directly from the integrated color picker.
- 📦 **Zero Dependencies**: Pure Python implementation using core QGIS APIs—no external library installation required.

---

## 🚀 Installation

### Option 1: Manual Installation (Recommended for Developers)

1.  **Clone/Download** this repository.
2.  Copy the `tower_spotter` folder into your QGIS plugins directory:
    - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
    - **Windows**: `%AppData%\QGIS\QGIS3\profiles\default\python\plugins\`
    - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3.  Restart QGIS.

### Option 2: QGIS Plugin Repository

1.  Open QGIS and go to **Plugins > Manage and Install Plugins...**.
2.  Search for **"Tower Spotter"**.
3.  Click **Install Plugin**.

---

## 📖 How to Use

1.  **Launch**: Open the plugin via the **Ineffable Tools** menu in the top menubar or the corresponding toolbar icon.
2.  **Input Selection**: Select an existing LineString layer from the dropdown, or click **Or Select KML File** to import an external route.
3.  **Configure Parameters**:
    - Set your desired **Radius** (e.g., 10m for typical footprint).
    - Set **Polygon Sides** (e.g., 6 for a hexagonal tower or 32+ for a circular footprint).
4.  **Style**: Choose your **Tower Color** and select either **Solid Fill** or **Outline Only**.
5.  **Process**: Click **Process** to generate the memory layer. The result will appear instantly on your canvas.
6.  **Export**: Click **Save Output** to export the result as a Google Earth compatible KML file.

---

## 👨‍💻 Author & License

- **Author**: [Vicky Sharma](https://github.com/ineffablexd)
- **Email**: vsharma@powergrid.in
- **License**: Licensed under [GPL-2.0-or-later](LICENSE)

<p align="center">
  Made with ❤️ by <a href="https://github.com/ineffablexd">Ineffable</a>
</p>
