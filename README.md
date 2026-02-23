# 🇪🇸 Spanish Companies Map

A desktop application to manage and visualize Spanish companies on an interactive map of Spain, built with Python.

## Features

- **Add, edit and delete companies** with their sector, province, autonomous community, coordinates and a link to their jobs page
- **Interactive map of Spain** with real province boundaries, powered by GeoPandas
- **Color-coded sectors** so each company type is easy to identify at a glance
- **Click to zoom** into any province on the map — click again or double-click to return to the full view
- **Click on a company marker** to select it in the table automatically
- **Persistent storage** using a local SQLite database — your data is saved between sessions
- **Automatic map download** — province geodata is downloaded once on first launch (~30 MB) and cached locally

## Sectors

| Sector | Color |
|--------|-------|
| Satellites | 🟡 Yellow |
| Defense & Space | 🟣 Pink |
| Communications | 🔴 Red |
| Aeronautics | 🔵 Cyan |
| Technology | 🔵 Blue |
| Consulting | 🔵 Dark Blue |
| Energy | 🟢 Green |
| Other | ⚪ Grey |

## Requirements

- Python 3.8 or higher
- The following Python libraries:

```bash
pip install geopandas matplotlib shapely
```

> `tkinter` and `sqlite3` are included with Python by default — no extra installation needed.

## How to Run

1. Clone or download this repository
2. Install the dependencies listed above
3. Run the main script:

```bash
python spanish_companies.py
```

On first launch, the app will automatically download the Spain province shapefile (~30 MB). This only happens once — subsequent launches will use the cached files.

## Project Structure

```
Companies-in-Spain/
│
├── spanish_companies.py     # Main application
├── README.md              # This file
│
├── empresas.db            # SQLite database (auto-created, not included in repo)
└── shapefiles_esp/        # Province geodata (auto-downloaded, not included in repo)
```

## Usage

### Adding a company
1. Fill in the company name, sector and province using the form on the left
2. The autonomous community field fills in automatically based on the selected province
3. Enter the exact **latitude and longitude** of the company (the province selection does not set these automatically — this allows precise placement within a province)
4. Optionally add a link to the company's jobs page
5. Click **Añadir**

### Editing a company
1. Click on a company in the table or on its marker on the map
2. Modify any fields in the form
3. Click **Guardar**

### Map interaction
- **Single click** on a province → zooms into that province
- **Single click again** on the same province, or **double click** anywhere → returns to full Spain view
- **"Vista completa" button** → also returns to full view
- **Click on a company marker** → selects it in the table and loads its data into the form

## Notes

- The `empresas.db` database file and the `shapefiles_esp/` folder are generated locally and are **not included in this repository**
- If you need to place a company that does not belong to any listed province, select **"Otra"** and enter the coordinates manually
