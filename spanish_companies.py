"""
Gestion de Empresas Espanolas
- Base de datos SQLite con provincia y comunidad autonoma
- Migracion automatica si la BD ya existia con el campo 'ciudad'
- Mapa geografico real de Espana con provincias (GeoPandas)
- Zoom a provincia al hacer clic en el mapa
- Interfaz tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import webbrowser
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geopandas as gpd
import os
import zipfile
import urllib.request

# ==============================================================
# DATOS GEOGRAFICOS: provincias y sus comunidades autonomas
# ==============================================================
# Cada entrada: "Nombre provincia": ("Comunidad Autonoma", longitud, latitud)
PROVINCIAS = {
    "A Coruna":          ("Galicia",              -8.4115, 43.3623),
    "Albacete":          ("Castilla-La Mancha",   -1.8585, 38.9943),
    "Alicante":          ("Comunidad Valenciana", -0.4810, 38.3452),
    "Almeria":           ("Andalucia",            -2.4637, 36.8381),
    "Asturias":          ("Asturias",             -5.8449, 43.3614),
    "Avila":             ("Castilla y Leon",      -4.7114, 40.6566),
    "Badajoz":           ("Extremadura",          -6.9706, 38.8794),
    "Barcelona":         ("Cataluna",              2.1734, 41.3851),
    "Bizkaia":           ("Pais Vasco",           -2.9253, 43.2630),
    "Burgos":            ("Castilla y Leon",      -3.6969, 42.3439),
    "Caceres":           ("Extremadura",          -6.3724, 39.4753),
    "Cadiz":             ("Andalucia",            -6.2894, 36.5271),
    "Cantabria":         ("Cantabria",            -3.8044, 43.4623),
    "Castellon":         ("Comunidad Valenciana", -0.0524, 39.9864),
    "Ceuta":             ("Ceuta",                -5.3162, 35.8894),
    "Ciudad Real":       ("Castilla-La Mancha",   -3.9289, 38.9848),
    "Cordoba":           ("Andalucia",            -4.7794, 37.8882),
    "Cuenca":            ("Castilla-La Mancha",   -2.1374, 40.0704),
    "Gipuzkoa":          ("Pais Vasco",           -2.0000, 43.1500),
    "Girona":            ("Cataluna",              2.8214, 41.9794),
    "Granada":           ("Andalucia",            -3.5986, 37.1773),
    "Guadalajara":       ("Castilla-La Mancha",   -3.1614, 40.6322),
    "Huelva":            ("Andalucia",            -6.9447, 37.2614),
    "Huesca":            ("Aragon",               -0.4082, 42.1401),
    "Illes Balears":     ("Islas Baleares",        2.6502, 39.5696),
    "Jaen":              ("Andalucia",            -3.7903, 37.7796),
    "La Rioja":          ("La Rioja",             -2.4450, 42.4650),
    "Las Palmas":        ("Canarias",            -15.4138, 28.1235),
    "Leon":              ("Castilla y Leon",      -5.5671, 42.5987),
    "Lleida":            ("Cataluna",              0.6217, 41.6148),
    "Lugo":              ("Galicia",              -7.5560, 43.0097),
    "Madrid":            ("Madrid",               -3.7038, 40.4168),
    "Malaga":            ("Andalucia",            -4.4214, 36.7213),
    "Melilla":           ("Melilla",              -2.9388, 35.2923),
    "Murcia":            ("Murcia",               -1.1307, 37.9922),
    "Navarra":           ("Navarra",              -1.6440, 42.8125),
    "Ourense":           ("Galicia",              -7.8640, 42.3360),
    "Palencia":          ("Castilla y Leon",      -4.5288, 42.0097),
    "Pontevedra":        ("Galicia",              -8.6455, 42.4337),
    "Salamanca":         ("Castilla y Leon",      -5.6640, 40.9701),
    "Santa Cruz de Tenerife": ("Canarias",       -16.2519, 28.4636),
    "Segovia":           ("Castilla y Leon",      -4.1184, 40.9429),
    "Sevilla":           ("Andalucia",            -5.9845, 37.3891),
    "Soria":             ("Castilla y Leon",      -2.4638, 41.7636),
    "Tarragona":         ("Cataluna",              1.2445, 41.1189),
    "Teruel":            ("Aragon",               -1.1065, 40.3456),
    "Toledo":            ("Castilla-La Mancha",   -4.0273, 39.8628),
    "Valencia":          ("Comunidad Valenciana", -0.3763, 39.4699),
    "Valladolid":        ("Castilla y Leon",      -4.7245, 41.6523),
    "Zamora":            ("Castilla y Leon",      -5.7448, 41.5036),
    "Zaragoza":          ("Aragon",               -0.8773, 41.6561),
    "Alava":             ("Pais Vasco",           -2.6726, 42.8467),
    "Otra":              (None,                    None,   None),
}

NOMBRES_PROVINCIAS = list(PROVINCIAS.keys())

SECTORES = [
    "Satelites", "Defensa y Espacio",
    "Comunicaciones", "Aeronautica",
    "Tecnologia", "Consultoria",
    "Energia", "Otro"
]

SECTOR_COLORES = {
    "Satelites":         "#efd90d",
    "Defensa y Espacio": "#ef0dd1",
    "Comunicaciones":    "#f82e0a",
    "Aeronautica":       "#07dfef",
    "Tecnologia":        "#4e79a7",
    "Consultoria":       "#0e53e8",
    "Energia":           "#66ed0d",
    "Otro":              "#aaaaaa",
}

DB_PATH = "empresas.db"

# ==============================================================
# GEODATOS DE PROVINCIAS ESPANOLAS
# ==============================================================
SHAPEFILE_DIR  = "shapefiles_esp"
SHAPEFILE_PATH = os.path.join(SHAPEFILE_DIR, "gadm41_ESP_2.shp")
SHAPEFILE_URL  = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_ESP_shp.zip"

def _ensure_shapefile():
    if os.path.exists(SHAPEFILE_PATH):
        return True
    os.makedirs(SHAPEFILE_DIR, exist_ok=True)
    zip_path = os.path.join(SHAPEFILE_DIR, "gadm41_ESP_shp.zip")
    try:
        print("Descargando mapa de provincias (~30 MB), espera un momento...")
        urllib.request.urlretrieve(SHAPEFILE_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(SHAPEFILE_DIR)
        os.remove(zip_path)
        print("Mapa descargado correctamente.")
        return True
    except Exception as e:
        print(f"Error descargando shapefile: {e}")
        return False

def load_geodata():
    if not _ensure_shapefile():
        return None
    try:
        return gpd.read_file(SHAPEFILE_PATH)
    except Exception as e:
        print(f"Error cargando shapefile: {e}")
        return None

# ==============================================================
# BASE DE DATOS + MIGRACION AUTOMATICA
# ==============================================================
def init_db():
    """
    Crea la tabla si no existe.
    Si ya existia con el campo 'ciudad' (version antigua),
    la migra anadiendo 'provincia' y 'comunidad' sin borrar datos.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Comprobar si la tabla ya existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empresas'")
    tabla_existe = cur.fetchone() is not None

    if tabla_existe:
        # Leer columnas actuales
        cur.execute("PRAGMA table_info(empresas)")
        columnas = [row[1] for row in cur.fetchall()]

        # --- MIGRACION: si tiene 'ciudad' pero no 'provincia' ---
        if "ciudad" in columnas and "provincia" not in columnas:
            print("Migrando base de datos al nuevo esquema...")
            # 1. Anadir columnas nuevas
            cur.execute("ALTER TABLE empresas ADD COLUMN provincia TEXT")
            cur.execute("ALTER TABLE empresas ADD COLUMN comunidad TEXT")
            # 2. Copiar 'ciudad' a 'provincia' para no perder el dato
            cur.execute("UPDATE empresas SET provincia = ciudad")
            # 3. Intentar rellenar 'comunidad' a partir de la provincia
            cur.execute("SELECT id, provincia FROM empresas")
            filas = cur.fetchall()
            for emp_id, prov in filas:
                datos = PROVINCIAS.get(prov)
                if datos and datos[0]:
                    cur.execute(
                        "UPDATE empresas SET comunidad=? WHERE id=?",
                        (datos[0], emp_id)
                    )
            con.commit()
            print("Migracion completada. Revisa las empresas para confirmar provincia/comunidad.")

        # --- MIGRACION: si no tiene latitud/longitud (muy antigua) ---
        if "latitud" not in columnas:
            cur.execute("ALTER TABLE empresas ADD COLUMN latitud REAL")
        if "longitud" not in columnas:
            cur.execute("ALTER TABLE empresas ADD COLUMN longitud REAL")

    else:
        # Crear tabla nueva con el esquema completo
        cur.execute("""
            CREATE TABLE empresas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT NOT NULL,
                sector      TEXT,
                provincia   TEXT,
                comunidad   TEXT,
                latitud     REAL NOT NULL,
                longitud    REAL NOT NULL,
                link_empleados TEXT
            )
        """)

    con.commit()
    con.close()

def get_all():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT id, nombre, sector, provincia, comunidad, latitud, longitud, link_empleados "
        "FROM empresas ORDER BY nombre"
    )
    rows = cur.fetchall()
    con.close()
    return rows

def insert_empresa(nombre, sector, provincia, comunidad, lat, lon, link):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO empresas (nombre, sector, provincia, comunidad, latitud, longitud, link_empleados) "
        "VALUES (?,?,?,?,?,?,?)",
        (nombre, sector, provincia, comunidad, lat, lon, link)
    )
    con.commit()
    con.close()

def delete_empresa(emp_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM empresas WHERE id=?", (emp_id,))
    con.commit()
    con.close()

def update_empresa(emp_id, nombre, sector, provincia, comunidad, lat, lon, link):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "UPDATE empresas SET nombre=?, sector=?, provincia=?, comunidad=?, "
        "latitud=?, longitud=?, link_empleados=? WHERE id=?",
        (nombre, sector, provincia, comunidad, lat, lon, link, emp_id)
    )
    con.commit()
    con.close()

# ==============================================================
# APLICACION PRINCIPAL
# ==============================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Empresas Espanolas")
        self.geometry("1350x780")
        self.configure(bg="#f0f0f0")
        self.resizable(True, True)

        init_db()
        self._selected_id    = None
        self._empresa_data   = []
        self._gdf            = None
        self._zoomed_prov    = None   # None = vista completa; str = NAME_2 en zoom

        self._build_ui()

        self._gdf = load_geodata()
        if self._gdf is None:
            messagebox.showwarning(
                "Mapa no disponible",
                "No se pudo descargar el mapa de provincias.\n"
                "Comprueba tu conexion a internet y reinicia el programa."
            )

        self._draw_map()
        self._refresh_table()

    # ----------------------------------------------------------
    # INTERFAZ
    # ----------------------------------------------------------
    def _build_ui(self):
        left = tk.Frame(self, bg="#f0f0f0", width=510)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        left.pack_propagate(False)

        form = tk.LabelFrame(
            left, text="  Datos de la empresa  ", bg="#f0f0f0",
            font=("Helvetica", 11, "bold"), padx=10, pady=8
        )
        form.pack(fill=tk.X)

        # Fila 0: Nombre
        tk.Label(form, text="Nombre:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=3)
        self.ent_nombre = tk.Entry(form, font=("Helvetica", 10))
        self.ent_nombre.grid(row=0, column=1, columnspan=3, sticky="ew", pady=3, padx=(6,0))

        # Fila 1: Sector
        tk.Label(form, text="Sector:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=3)
        self.cmb_sector = ttk.Combobox(form, values=SECTORES, state="readonly", font=("Helvetica", 10))
        self.cmb_sector.grid(row=1, column=1, columnspan=3, sticky="ew", pady=3, padx=(6,0))

        # Fila 2: Provincia (desplegable)
        tk.Label(form, text="Provincia:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=3)
        self.cmb_provincia = ttk.Combobox(form, values=NOMBRES_PROVINCIAS, state="readonly", font=("Helvetica", 10))
        self.cmb_provincia.grid(row=2, column=1, columnspan=3, sticky="ew", pady=3, padx=(6,0))
        self.cmb_provincia.bind("<<ComboboxSelected>>", self._on_provincia_change)

        # Fila 3: Comunidad (se rellena sola, pero editable)
        tk.Label(form, text="Comunidad:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=3, column=0, sticky="w", pady=3)
        self.ent_comunidad = tk.Entry(form, font=("Helvetica", 10), state="readonly")
        self.ent_comunidad.grid(row=3, column=1, columnspan=3, sticky="ew", pady=3, padx=(6,0))

        # Fila 4: Latitud y Longitud (siempre visibles, obligatorios)
        tk.Label(form, text="Latitud:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=4, column=0, sticky="w", pady=3)
        self.ent_lat = tk.Entry(form, font=("Helvetica", 10))
        self.ent_lat.grid(row=4, column=1, sticky="ew", pady=3, padx=(6,0))
        tk.Label(form, text="Longitud:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=4, column=2, sticky="w", pady=3, padx=(10,0))
        self.ent_lon = tk.Entry(form, font=("Helvetica", 10))
        self.ent_lon.grid(row=4, column=3, sticky="ew", pady=3, padx=(6,0))

        # Fila 5: Link empleados
        tk.Label(form, text="Link empleados:", bg="#f0f0f0", font=("Helvetica", 10)).grid(row=5, column=0, sticky="w", pady=3)
        self.ent_link = tk.Entry(form, font=("Helvetica", 10))
        self.ent_link.grid(row=5, column=1, columnspan=3, sticky="ew", pady=3, padx=(6,0))

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Nota informativa sobre coordenadas
        tk.Label(
            form,
            text="Las coordenadas se rellenan solas al elegir provincia. Ajustalas si la empresa\n"
                 "no esta en la capital de provincia. Selecciona 'Otra' para introducirlas a mano.",
            bg="#f0f0f0", font=("Helvetica", 8), fg="#666", justify="left"
        ).grid(row=6, column=0, columnspan=4, sticky="w", pady=(2,0))

        # Botones
        btn_frame = tk.Frame(form, bg="#f0f0f0")
        btn_frame.grid(row=7, column=0, columnspan=4, pady=(10, 0))
        botones = [
            ("Anadir",     self._add,       "#4CAF50"),
            ("Guardar",    self._update,    "#2196F3"),
            ("Eliminar",   self._delete,    "#f44336"),
            ("Abrir link", self._open_link, "#9c27b0"),
        ]
        for texto, cmd, color in botones:
            tk.Button(
                btn_frame, text=texto, command=cmd,
                bg=color, fg="white", font=("Helvetica", 10, "bold"),
                relief=tk.FLAT, padx=10
            ).pack(side=tk.LEFT, padx=4)

        # Tabla
        table_frame = tk.LabelFrame(
            left, text="  Empresas registradas  ", bg="#f0f0f0",
            font=("Helvetica", 11, "bold"), padx=5, pady=5
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        cols = ("ID", "Nombre", "Sector", "Provincia", "Comunidad")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        self.tree.heading("ID",        text="ID")
        self.tree.heading("Nombre",    text="Nombre")
        self.tree.heading("Sector",    text="Sector")
        self.tree.heading("Provincia", text="Provincia")
        self.tree.heading("Comunidad", text="Comunidad")
        self.tree.column("ID",        width=30,  anchor="center")
        self.tree.column("Nombre",    width=140)
        self.tree.column("Sector",    width=110)
        self.tree.column("Provincia", width=100)
        self.tree.column("Comunidad", width=130)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Panel derecho: mapa
        right = tk.Frame(self, bg="#f0f0f0")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        header = tk.Frame(right, bg="#f0f0f0")
        header.pack(fill=tk.X)
        self.lbl_mapa = tk.Label(
            header, text="Mapa de Espana - Provincias",
            font=("Helvetica", 12, "bold"), bg="#f0f0f0"
        )
        self.lbl_mapa.pack(side=tk.LEFT, expand=True)
        tk.Button(
            header, text="Vista completa", command=self._reset_zoom,
            bg="#607d8b", fg="white", font=("Helvetica", 9), relief=tk.FLAT, padx=8
        ).pack(side=tk.RIGHT)

        tk.Label(
            right,
            text="Clic en provincia = zoom  |  Doble clic o 'Vista completa' = volver",
            font=("Helvetica", 8), bg="#f0f0f0", fg="#666"
        ).pack()

        self.fig, self.ax = plt.subplots(figsize=(8, 6.5))
        self.fig.patch.set_facecolor("#4a90c4")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self._on_map_click)

    def _on_provincia_change(self, _event=None):
        """Al elegir provincia, rellena SOLO la comunidad autonoma.
        Las coordenadas las introduce siempre el usuario manualmente."""
        prov = self.cmb_provincia.get()
        datos = PROVINCIAS.get(prov)
        self.ent_comunidad.config(state=tk.NORMAL)
        self.ent_comunidad.delete(0, tk.END)
        if datos and datos[0]:
            comunidad, _, _ = datos
            self.ent_comunidad.insert(0, comunidad)
        self.ent_comunidad.config(state="readonly")

    # ----------------------------------------------------------
    # ZOOM POR PROVINCIA
    # ----------------------------------------------------------
    def _bbox_provincia(self, nombre_provincia):
        """Calcula el bounding box de una provincia con margen."""
        if self._gdf is None:
            return None
        subset = self._gdf[self._gdf["NAME_2"] == nombre_provincia]
        if subset.empty:
            return None
        b = subset.total_bounds  # [minx, miny, maxx, maxy]
        mx = max((b[2] - b[0]) * 0.15, 0.2)
        my = max((b[3] - b[1]) * 0.15, 0.2)
        return (b[0]-mx, b[1]-my, b[2]+mx, b[3]+my)

    def _provincia_en_punto(self, x, y):
        """Devuelve el NAME_2 de la provincia donde cayo el clic, o None."""
        if self._gdf is None:
            return None
        from shapely.geometry import Point
        pt = Point(x, y)
        for _, row in self._gdf.iterrows():
            if row.geometry and row.geometry.contains(pt):
                return row["NAME_2"]
        return None

    # ----------------------------------------------------------
    # DIBUJO DEL MAPA
    # ----------------------------------------------------------
    def _draw_map(self):
        self.ax.clear()
        for ax_extra in self.fig.axes[1:]:
            self.fig.delaxes(ax_extra)

        if self._gdf is not None:
            if self._zoomed_prov:
                # Todas las provincias en gris
                self._gdf.plot(ax=self.ax, color="#c8c8c8", edgecolor="#999", linewidth=0.5, zorder=1)
                # Provincia seleccionada en verde
                subset = self._gdf[self._gdf["NAME_2"] == self._zoomed_prov]
                subset.plot(ax=self.ax, color="#e8f0d8", edgecolor="#7a9a60", linewidth=1.2, zorder=2)
                # Zoom al bbox de la provincia
                bbox = self._bbox_provincia(self._zoomed_prov)
                if bbox:
                    self.ax.set_xlim(bbox[0], bbox[2])
                    self.ax.set_ylim(bbox[1], bbox[3])
                self.lbl_mapa.config(text=f"Provincia: {self._zoomed_prov}")
            else:
                # Vista completa
                self._gdf.plot(ax=self.ax, color="#e8f0d8", edgecolor="#7a9a60", linewidth=0.6, zorder=1)
                self.ax.set_xlim(-9.5, 4.5)
                self.ax.set_ylim(35.8, 44.0)
                self.lbl_mapa.config(text="Mapa de Espana - Provincias")
                # Mini mapa Canarias
                ax_can = self.fig.add_axes([0.01, 0.01, 0.22, 0.22])
                ax_can.set_facecolor("#4a90c4")
                self._gdf.plot(ax=ax_can, color="#e8f0d8", edgecolor="#7a9a60", linewidth=0.5)
                ax_can.set_xlim(-18.5, -13.0)
                ax_can.set_ylim(27.6, 29.5)
                ax_can.set_aspect("equal")
                ax_can.axis("off")
                ax_can.set_title("Canarias", fontsize=7, pad=2, color="#444")
                for spine in ax_can.spines.values():
                    spine.set_visible(True)
                    spine.set_edgecolor("#aaa")
                    spine.set_linewidth(0.8)

            self.ax.set_facecolor("#4a90c4")
            self.ax.set_aspect("equal")
            self.ax.axis("off")
        else:
            self.ax.set_facecolor("#4a90c4")
            self.ax.set_xlim(-9.5, 4.5)
            self.ax.set_ylim(35.8, 44.0)
            self.ax.text(0, 40, "Mapa no disponible", ha="center", va="center", fontsize=10, color="#888")
            self.ax.axis("off")

        self._empresa_data = []
        self._plot_empresas()
        self.canvas.draw()

    def _plot_empresas(self):
        rows = get_all()
        self._empresa_data = []
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        for row in rows:
            emp_id, nombre, sector, provincia, comunidad, lat, lon, link = row
            if lat is None or lon is None:
                continue
            if not (xlim[0] <= lon <= xlim[1] and ylim[0] <= lat <= ylim[1]):
                continue

            # Normalizar tildes por si el sector fue guardado con una version antigua
            sector_norm = (sector or "")
            sector_norm = sector_norm.replace("é","e").replace("á","a").replace("í","i").replace("ó","o").replace("ú","u").replace("ó","o")
            color = SECTOR_COLORES.get(sector_norm, SECTOR_COLORES.get(sector, "#aaaaaa"))
            self.ax.plot(lon, lat, "o", color=color, markersize=10,
                         markeredgecolor="white", markeredgewidth=1.2, zorder=5)
            self.ax.annotate(
                nombre, (lon, lat), textcoords="offset points", xytext=(7, 5),
                fontsize=7, color="#111",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.6, ec="none"),
                zorder=6
            )
            self._empresa_data.append({"id": emp_id, "nombre": nombre, "lat": lat, "lon": lon})

        def _normalizar(s):
            return (s or "").replace("é","e").replace("á","a").replace("í","i").replace("ó","o").replace("ú","u")

        sectores_presentes = sorted({r[2] for r in rows if r[2]})
        handles = [
            mpatches.Patch(color=SECTOR_COLORES.get(_normalizar(s), SECTOR_COLORES.get(s, "#aaa")), label=s)
            for s in sectores_presentes
        ]
        if handles:
            self.ax.legend(handles=handles, loc="lower right", fontsize=7,
                           framealpha=0.85, title="Sectores", title_fontsize=7)

    def _refresh_map(self):
        self._draw_map()

    def _reset_zoom(self):
        self._zoomed_prov = None
        self._draw_map()

    def _on_map_click(self, event):
        if event.xdata is None or event.ydata is None:
            return
        if event.dblclick:
            self._reset_zoom()
            return

        # Comprobar si cayo cerca de una empresa
        min_dist = float("inf")
        closest  = None
        for emp in self._empresa_data:
            d = (emp["lon"] - event.xdata)**2 + (emp["lat"] - event.ydata)**2
            if d < min_dist:
                min_dist = d
                closest  = emp
        if closest and min_dist < 0.05:
            for item in self.tree.get_children():
                vals = self.tree.item(item, "values")
                if int(vals[0]) == closest["id"]:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
            return

        # Zoom a la provincia clickada
        prov = self._provincia_en_punto(event.xdata, event.ydata)
        if prov:
            if prov == self._zoomed_prov:
                self._reset_zoom()
            else:
                self._zoomed_prov = prov
                self._draw_map()

    # ----------------------------------------------------------
    # CRUD
    # ----------------------------------------------------------
    def _get_form_data(self):
        nombre    = self.ent_nombre.get().strip()
        sector    = self.cmb_sector.get()
        provincia = self.cmb_provincia.get()
        comunidad = self.ent_comunidad.get().strip()
        link      = self.ent_link.get().strip()
        try:
            lat = float(self.ent_lat.get())
            lon = float(self.ent_lon.get())
        except ValueError:
            messagebox.showerror("Error", "Latitud y longitud son obligatorias y deben ser numeros decimales.\nEjemplo: 40.4168")
            return None
        return nombre, sector, provincia, comunidad, lat, lon, link

    def _validate(self, nombre, provincia):
        if not nombre:
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio.")
            return False
        if not provincia:
            messagebox.showerror("Error", "Selecciona una provincia.")
            return False
        return True

    def _add(self):
        data = self._get_form_data()
        if data is None:
            return
        nombre, sector, provincia, comunidad, lat, lon, link = data
        if not self._validate(nombre, provincia):
            return
        insert_empresa(nombre, sector, provincia, comunidad, lat, lon, link)
        self._clear_form()
        self._refresh_table()
        self._refresh_map()

    def _update(self):
        if self._selected_id is None:
            messagebox.showinfo("Info", "Selecciona una empresa de la tabla primero.")
            return
        data = self._get_form_data()
        if data is None:
            return
        nombre, sector, provincia, comunidad, lat, lon, link = data
        if not self._validate(nombre, provincia):
            return
        update_empresa(self._selected_id, nombre, sector, provincia, comunidad, lat, lon, link)
        self._refresh_table()
        self._refresh_map()

    def _delete(self):
        if self._selected_id is None:
            messagebox.showinfo("Info", "Selecciona una empresa de la tabla primero.")
            return
        if messagebox.askyesno("Confirmar", "Eliminar esta empresa?"):
            delete_empresa(self._selected_id)
            self._selected_id = None
            self._clear_form()
            self._refresh_table()
            self._refresh_map()

    def _open_link(self):
        link = self.ent_link.get().strip()
        if not link:
            messagebox.showinfo("Info", "No hay link de empleados registrado.")
            return
        if not link.startswith("http"):
            link = "https://" + link
        webbrowser.open(link)

    def _clear_form(self):
        self.ent_nombre.delete(0, tk.END)
        self.cmb_sector.set("")
        self.cmb_provincia.set("")
        self.ent_comunidad.config(state=tk.NORMAL)
        self.ent_comunidad.delete(0, tk.END)
        self.ent_comunidad.config(state="readonly")
        self.ent_lat.delete(0, tk.END)
        self.ent_lon.delete(0, tk.END)
        self.ent_link.delete(0, tk.END)
        self._selected_id = None

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for row in get_all():
            self.tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4]))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        emp_id = int(self.tree.item(sel[0], "values")[0])
        self._selected_id = emp_id

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "SELECT nombre, sector, provincia, comunidad, latitud, longitud, link_empleados "
            "FROM empresas WHERE id=?", (emp_id,)
        )
        row = cur.fetchone()
        con.close()

        if row:
            nombre, sector, provincia, comunidad, lat, lon, link = row
            self._clear_form()
            self._selected_id = emp_id
            self.ent_nombre.insert(0, nombre or "")
            self.cmb_sector.set(sector or "")
            self.cmb_provincia.set(provincia or "")
            self.ent_comunidad.config(state=tk.NORMAL)
            self.ent_comunidad.insert(0, comunidad or "")
            self.ent_comunidad.config(state="readonly")
            self.ent_lat.insert(0, str(lat) if lat is not None else "")
            self.ent_lon.insert(0, str(lon) if lon is not None else "")
            self.ent_link.insert(0, link or "")


# ==============================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()
