# 🧭 Crossing Angel Analyser

[![QGIS Version](https://img.shields.io/badge/QGIS-3.0+-green.svg)](https://qgis.org/)
[![License](https://img.shields.io/badge/License-GPL--2.0--or--later-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](metadata.txt)

A professional, **QGIS plugin** designed for real-time intersection angle analysis between vector line layers. Part of the **Ineffable Tools** suite, this tool is essential for route planning, obstacle checking, and geometric validation.

---

## ⚡ Overview

The **Crossing Angel Analyser** dynamically calculates the intersection angles between a primary "Input Layer" (e.g., a proposed route) and multiple "Crossing Layers" (e.g., existing infrastructure, bee lines, or environmental buffers).

As you digitize or edit your route, the plugin automatically:

1. Detects every intersection point.
2. Calculates the precise angle of crossing.
3. Generates high-visibility, color-coded markers for instant visual feedback.

---

## 📸 Visual Workflow

### 1. Before Running

Start with your route and obstacle layers. No analysis has been performed yet.

<p align="center">
  <img src="assets/before_running.png" width="800" alt="Map before analysis">
</p>

### 2. Plugin Configuration

Open the **Ineffable Tools** menu and launch the analyser. Select your route and target layers.

<p align="center">
  <img src="assets/plugin_ui.png" width="400" alt="Plugin UI Configuration">
</p>

### 3. Real-Time Results

Instance analysis! See exactly where your route crosses obstacles and at what angle.

<p align="center">
  <img src="assets/after_running.png" width="800" alt="Map after analysis with angles">
</p>

---

## ✨ Key Features

- **🚀 Real-Time Processing:** Automatically updates as you move, edit, or add features to your route layer.
- **📊 Precise Calculations:** Calculates the geometric tangent at the exact point of intersection for curved lines.
- **🎨 Dynamic Style Engine:** Automatically styles the output "Angles" layer with color-coded markers:
  - 🔴 **CRITICAL (< 70°):** High impact crossing.
  - 🔵 **MODERATE (70° - 80°):** Standard crossing.
  - 🟢 **OPTIMAL (> 80°):** Near-perpendicular crossing.
- **🏗️ Memory Layer Architecture:** Uses lightning-fast memory layers for temporary analysis, avoiding file clutter.
- **🛠️ Multi-Layer Support:** Select multiple obstacle layers simultaneously for comprehensive checking.

---

## 🛠️ Installation

1. **Download/Clone:** Clone this repository or download the ZIP file.
2. **Locate Plugin Folder:** Open QGIS and go to `Settings` > `User Profiles` > `Open Active Profile Folder`. Navigate to `python/plugins`.
3. **Copy:** Extract the `crossing_angel_analyser` folder into the `plugins` directory.
4. **Enable:** Restart QGIS and enable **Crossing Angel Analyser** via the `Plugins` > `Manage and Install Plugins...` menu.

---

## 📖 How to Use

1. **Launch:** Locate the **Ineffable Tools** menu in your QGIS top bar and click **Crossing Angel Analyser**.
2. **Select Input Layer:** In the "Input Layer" dropdown, choose the line layer you are currently editing (e.g., _Proposed Route_).
3. **Select Crossing Layers:** Select one or more layers from the "Crossing Layers" list that you want to check for intersections.
4. **Enable Live Angles:** Click the **Enable Live Angles** button.
5. **Analyze:** A new layer named **"Angles"** will appear at the top of your layer list. Move your map or edit your lines to see the angles update in real-time.

---

## 👨‍💻 Author

**Vicky Sharma**  
📧 [vsharma@powergrid.in](mailto:vsharma@powergrid.in)  
🔗 [GitHub Profile](https://github.com/ineffablexd)

---

## 📜 License

This project is licensed under the **GNU General Public License v2.0 or later**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/ineffablexd">Ineffable</a>
</p>
