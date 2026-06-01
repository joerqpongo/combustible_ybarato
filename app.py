"""
combustible_ybarato.es — Buscador de combustible barato en España
Fuente de datos: Geoportal de Gasolineras (Ministerio para la Transición Ecológica)
"""
import math
import os
import time
import datetime
import requests
import pandas as pd
import streamlit as st
import html

# ─── Intentar importar streamlit-js-eval (opcional) ───────────────────────────
try:
    from streamlit_js_eval import get_geolocation
    JS_EVAL_AVAILABLE = True
except ImportError:
    JS_EVAL_AVAILABLE = False

# ─── Configuración de la página ───────────────────────────────────────────────
st.set_page_config(
    page_title="⛽ Combustible Barato España",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* ── Fuente global ── */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Fondo oscuro ── */
  .stApp { background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #0d0d2b 100%); }

  /* ── Quitar espacios superiores e inferiores del contenedor principal ── */
  .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
  }
  
  /* Cabecera transparente para mostrar el botón de menú lateral en pantallas pequeñas */
  [data-testid="stHeader"] {
    background: transparent !important;
  }
  [data-testid="stHeader"] button, [data-testid="stHeader"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
  }

  /* ── Quitar espacio superior de la barra lateral ── */
  [data-testid="stSidebarContent"] {
    padding-top: 0.1rem !important;
  }
  [data-testid="stSidebarContent"] [data-testid="stSidebarUserContent"] {
    padding-top: 0rem !important;
  }

  /* Reducir márgenes por defecto de elementos de Streamlit y compactar barra lateral */
  div[data-testid="stElementContainer"] {
    margin-bottom: 0.3rem !important;
  }
  [data-testid="stSidebar"] div[data-testid="stElementContainer"] {
    margin-bottom: 0.15rem !important;
  }
  
  /* Compactar títulos en la barra lateral */
  [data-testid="stSidebar"] h2 {
    margin-top: 0.1rem !important;
    margin-bottom: 0.1rem !important;
    font-size: 1.15rem !important;
    font-weight: 700;
  }

  /* Compactar el padding interno de los widgets en la sidebar */
  [data-testid="stSidebar"] .stSelectbox, 
  [data-testid="stSidebar"] .stSlider, 
  [data-testid="stSidebar"] .stRadio, 
  [data-testid="stSidebar"] .stTextInput, 
  [data-testid="stSidebar"] .stNumberInput {
    margin-bottom: 0.1rem !important;
  }

  /* ── Hero header compactado ── */
  .hero-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #6a3093 100%);
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 0.8rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(42,82,152,0.3);
    border: 1px solid rgba(255,255,255,0.1);
  }
  .hero-header h1 {
    font-size: clamp(1.3rem, 3.5vw, 1.8rem); font-weight: 800; color: #fff;
    margin: 0; letter-spacing: -0.5px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
  }
  .hero-header p { color: rgba(255,255,255,0.8); font-size: clamp(0.75rem, 1.5vw, 0.85rem); margin: 0.2rem 0 0; }

  /* ── Metric cards ── */
  .metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 0.8rem 0.6rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.3); }
  .metric-card .label { color: rgba(255,255,255,0.6); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; }
  .metric-card .value { color: #fff; font-size: clamp(1.1rem, 2.5vw, 1.4rem); font-weight: 700; margin-top: 0.1rem; }
  .metric-card .sub   { color: #6ee7b7; font-size: 0.75rem; margin-top: 0.1rem; }

  /* ── Tabla de resultados responsiva ── */
  .table-container {
    width: 100%;
    overflow-x: auto;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.02);
    margin: 0.6rem 0 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    color: #e2e8f0;
  }
  .results-table th, .results-table td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    white-space: nowrap;
  }
  .results-table th {
    background-color: rgba(255,255,255,0.06);
    font-weight: 600;
    color: #fff;
    border-bottom: 2px solid rgba(255,255,255,0.15);
  }
  .results-table tr:hover {
    background-color: rgba(255,255,255,0.04);
  }
  .stDataFrame { border-radius: 10px !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: rgba(15,12,41,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  /* ── Botones ── */
  .stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff !important; border: none; border-radius: 8px;
    font-weight: 600; padding: 0.4rem 1.2rem;
    transition: all 0.2s;
  }
  .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }

  /* ── Badge precio más bajo ── */
  .badge-low  { background: #065f46; color: #6ee7b7; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600; }
  .badge-high { background: #7f1d1d; color: #fca5a5; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600; }

  /* ── Alertas info ── */
  .info-box {
    background: rgba(99,179,237,0.12); border-left: 4px solid #63b3ed;
    border-radius: 6px; padding: 0.5rem 0.7rem; margin: 0.4rem 0;
    color: #bee3f8; font-size: 0.8rem;
  }

  /* ── Enlace Maps ── */
  a.maps-link {
    background: rgba(66,153,225,0.2); color: #90cdf4 !important;
    text-decoration: none; border-radius: 5px; padding: 2px 6px;
    font-size: 0.78rem; transition: background 0.2s;
  }
  a.maps-link:hover { background: rgba(66,153,225,0.4); }

  /* ── Status chip ── */
  .status-ok   { color: #6ee7b7; font-weight: 600; font-size: 0.82rem; }
  .status-warn { color: #fbbf24; font-weight: 600; font-size: 0.82rem; }

  /* ── Divider ── */
  .custom-divider { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 0.3rem 0; }

  /* ── Barra de estado superior ── */
  .top-status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.4rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.82rem;
    color: #e2e8f0;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .top-status-item {
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }

  /* ── Ajustes responsive específicos para móviles/tablets ── */
  @media (max-width: 768px) {
    .hero-header {
      padding: 0.8rem 1rem;
      margin-bottom: 0.6rem;
      border-radius: 8px;
    }
    .metric-card {
      padding: 0.6rem 0.5rem;
      margin-bottom: 0.6rem;
    }
  }
</style>
""", unsafe_allow_html=True)

# ─── Constantes ───────────────────────────────────────────────────────────────
DATA_URL     = "https://geoportalgasolineras.es/geoportal/resources/files/preciosEESS_es.xls"
LOCAL_FILE   = "preciosEESS_es.xls"
CACHE_KEY    = "gasolineras_df"
LOADED_AT_KEY = "gasolineras_loaded_at"

COMBUSTIBLES = {
    "Gasolina 95 E5":              "Precio gasolina 95 E5",
    "Gasolina 95 E5 Premium":      "Precio gasolina 95 E5 Premium",
    "Gasolina 98 E5":              "Precio gasolina 98 E5",
    "Gasolina 95 E25":             "Precio gasolina 95 E25",
    "Gasolina 95 E85":             "Precio gasolina 95 E85",
    "Gasóleo A":                   "Precio gasóleo A",
    "Gasóleo Premium":             "Precio gasóleo Premium",
    "Gasóleo B":                   "Precio gasóleo B",
    "Gasóleo C":                   "Precio gasóleo C",
    "Gas Natural Comprimido":      "Precio gas natural comprimido",
    "Gas Natural Licuado":         "Precio gas natural licuado",
    "Gases Licuados del Petróleo": "Precio gases licuados del petróleo",
    "Hidrógeno":                   "Precio hidrógeno",
    "Biodiesel":                   "Precio biodiesel",
    "AdBlue":                      "Precio AdBlue",
    "Diesel Renovable":            "Precio diesel renovable",
    "Gasolina Renovable":          "Precio gasolina renovable",
}

# Coordenadas por defecto (Puerta del Sol, Madrid)
DEFAULT_LAT = 40.4168
DEFAULT_LON = -3.7038


# ─── Haversine ────────────────────────────────────────────────────────────────
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en km entre dos puntos GPS usando la fórmula de Haversine."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ─── Descarga y caché de datos ────────────────────────────────────────────────
def _needs_refresh() -> bool:
    """
    Devuelve True si hay que descargar datos nuevos.
    Lógica: si son >= 06:00 y los datos son del día anterior (o no existen).
    """
    now = datetime.datetime.now()
    if LOADED_AT_KEY not in st.session_state:
        return True
    loaded_at: datetime.datetime = st.session_state[LOADED_AT_KEY]
    # Umbral de actualización: las 06:00 AM de hoy
    cutoff = now.replace(hour=6, minute=0, second=0, microsecond=0)
    data_is_old = loaded_at.date() < now.date()
    after_cutoff = now >= cutoff
    return data_is_old and after_cutoff


def _parse_float(value) -> float:
    """Convierte string con coma decimal o NaN a float."""
    if pd.isna(value):
        return float("nan")
    try:
        return float(str(value).replace(",", ".").strip())
    except (ValueError, TypeError):
        return float("nan")


@st.cache_data(ttl=3600, show_spinner=False)
def _load_from_url(url: str) -> pd.DataFrame:
    """Descarga y parsea el Excel del Geoportal. Cacheado 1 hora por Streamlit."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with open(LOCAL_FILE, "wb") as f:
        f.write(resp.content)
    return _parse_excel(LOCAL_FILE)


def _parse_excel(filepath: str) -> pd.DataFrame:
    """Lee el XLS del Geoportal y limpia los datos."""
    # La cabecera real está en la fila 4 del fichero (índice 3 en pandas)
    df = pd.read_excel(filepath, engine="xlrd", header=3)

    # Limpiar espacios en nombres de columna (xlrd ya entrega UTF-8 correcto)
    df.columns = df.columns.str.strip()

    # Columnas de coordenadas
    for col in ["Latitud", "Longitud"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_float)

    # Columnas de precios: todas las que empiezan por "Precio" (case-insensitive)
    precio_cols = [c for c in df.columns if c.strip().lower().startswith("precio")]
    for col in precio_cols:
        df[col] = df[col].apply(_parse_float)

    # Verificar que existen las columnas de coordenadas
    if "Latitud" not in df.columns or "Longitud" not in df.columns:
        raise ValueError(
            f"No se encontraron columnas de coordenadas. Columnas disponibles: {list(df.columns)}"
        )

    # Eliminar filas sin coordenadas válidas
    df = df.dropna(subset=["Latitud", "Longitud"])
    df = df[df["Latitud"].between(-90, 90) & df["Longitud"].between(-180, 180)]

    return df.reset_index(drop=True)


def get_data() -> pd.DataFrame:
    """Obtiene el DataFrame gestionando la caché de sesión + descarga automática."""
    if _needs_refresh() or CACHE_KEY not in st.session_state:
        with st.spinner("🔄 Descargando datos actualizados del Geoportal…"):
            try:
                df = _load_from_url(DATA_URL)
                st.session_state[CACHE_KEY]    = df
                st.session_state[LOADED_AT_KEY] = datetime.datetime.now()
            except Exception as e:
                # Intentar con fichero local si existe
                if os.path.exists(LOCAL_FILE):
                    st.warning(f"⚠️ No se pudo descargar el fichero online ({e}). Usando datos locales.")
                    df = _parse_excel(LOCAL_FILE)
                    st.session_state[CACHE_KEY]    = df
                    st.session_state[LOADED_AT_KEY] = datetime.datetime.now()
                else:
                    st.error(f"❌ Error al descargar los datos y no hay fichero local: {e}")
                    st.stop()
    return st.session_state[CACHE_KEY]


# ─── Búsqueda de estaciones ───────────────────────────────────────────────────
def buscar_estaciones(
    df: pd.DataFrame,
    lat: float, lon: float,
    radio_km: float,
    col_precio: str,
    max_resultados: int = 50,
    ordenar_por: str = "Precio",
) -> pd.DataFrame:
    """Filtra estaciones en el radio dado con precio disponible, calcula distancia y ordena por el criterio elegido."""
    # Columna de precio puede no existir si el combustible no está en el dataset
    if col_precio not in df.columns:
        return pd.DataFrame()

    sub = df[df[col_precio].notna() & (df[col_precio] > 0)].copy()
    if sub.empty:
        return pd.DataFrame()

    sub["Distancia (km)"] = sub.apply(
        lambda r: haversine(lat, lon, r["Latitud"], r["Longitud"]), axis=1
    )
    sub = sub[sub["Distancia (km)"] <= radio_km]
    if sub.empty:
        return pd.DataFrame()

    if ordenar_por == "Precio":
        sub = sub.sort_values([col_precio, "Distancia (km)"], ascending=[True, True]).head(max_resultados)
    else:
        sub = sub.sort_values(["Distancia (km)", col_precio], ascending=[True, True]).head(max_resultados)

    # Columna enlace Maps
    sub["📍 Maps"] = sub.apply(
        lambda r: f'<a class="maps-link" href="https://www.google.com/maps/search/?api=1&query={r["Latitud"]},{r["Longitud"]}" target="_blank">Ver mapa</a>',
        axis=1
    )
    return sub.reset_index(drop=True)


# ─── Geolocalización desde el navegador ───────────────────────────────────────
def get_browser_location() -> tuple[float | None, float | None]:
    """Intenta obtener la ubicación del navegador usando streamlit-js-eval."""
    if not JS_EVAL_AVAILABLE:
        return None, None
    try:
        loc = get_geolocation()
        if loc and "coords" in loc:
            return loc["coords"]["latitude"], loc["coords"]["longitude"]
    except Exception:
        pass
    return None, None


# ─── Geocodificación por nombre (Nominatim) ───────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def geocode_place(place: str) -> tuple[float | None, float | None]:
    """Geocodifica un nombre de lugar usando la API de Nominatim (OpenStreetMap)."""
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place + ", España", "format": "json", "limit": 1},
            headers={"User-Agent": "combustible_ybarato_es/1.0"},
            timeout=10,
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Carga de datos ──
    df = get_data()
    loaded_at: datetime.datetime = st.session_state.get(LOADED_AT_KEY, datetime.datetime.now())

    # ── Sidebar: configuración ──
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")

        # Botón de actualización manual justo debajo de la cabecera
        if st.button("🔄 Actualizar datos ahora", use_container_width=True):
            _load_from_url.clear()
            if CACHE_KEY in st.session_state:
                del st.session_state[CACHE_KEY]
            if LOADED_AT_KEY in st.session_state:
                del st.session_state[LOADED_AT_KEY]
            st.rerun()

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # Tipo de combustible
        combustible_nombre = st.selectbox(
            "🛢️ Tipo de combustible",
            list(COMBUSTIBLES.keys()),
            index=0,
        )
        col_precio = COMBUSTIBLES[combustible_nombre]

        # Radio de búsqueda
        radio_km = st.slider("📡 Radio de búsqueda (km)", 1, 50, 10, 1)

        # Número de resultados
        max_res = st.slider("📊 Máx. resultados", 10, 100, 10, 5)

        # Criterio de ordenación
        criterio_orden = st.selectbox(
            "🔃 Ordenar resultados por",
            ["Precio (más barato primero)", "Distancia (más cercano primero)"],
            index=0,
        )

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        st.markdown("## 📍 Tu ubicación")

        # Ubicación
        metodo_ubicacion = st.radio(
            "Método de localización",
            ["🌐 Automática (GPS)", "🔍 Buscar ciudad", "🗺️ Coordenadas manuales"],
            index=0,
        )

        lat_user, lon_user = None, None
        location_label = ""
        location_status_text = ""

        if metodo_ubicacion == "🌐 Automática (GPS)":
            if JS_EVAL_AVAILABLE:
                lat_user, lon_user = get_browser_location()
                if lat_user and lon_user:
                    location_label = f"GPS: {lat_user:.4f}, {lon_user:.4f}"
                    location_status_text = "✅ GPS obtenido correctamente"
                else:
                    location_status_text = "⚠️ GPS no disponible, usando Madrid"
                    lat_user, lon_user = DEFAULT_LAT, DEFAULT_LON
                    location_label = "Madrid (defecto)"
            else:
                location_status_text = "ℹ️ GPS no disponible (usando Madrid)"
                lat_user, lon_user = DEFAULT_LAT, DEFAULT_LON
                location_label = "Madrid (defecto)"

        elif metodo_ubicacion == "🔍 Buscar ciudad":
            ciudad = st.text_input("Ciudad o municipio", placeholder="Ej: Sevilla, Zaragoza…")
            if ciudad:
                with st.spinner("Geocodificando…"):
                    lat_user, lon_user = geocode_place(ciudad)
                if lat_user:
                    location_label = ciudad.title()
                    location_status_text = f"✅ Ciudad: {location_label}"
                else:
                    location_status_text = "❌ Ciudad no encontrada (usando Madrid)"
                    lat_user, lon_user = DEFAULT_LAT, DEFAULT_LON
                    location_label = "Madrid (defecto)"
            else:
                lat_user, lon_user = DEFAULT_LAT, DEFAULT_LON
                location_label = "Madrid (defecto)"
                location_status_text = "🔍 Ingresa una ciudad para buscar"

        else:  # Coordenadas manuales
            lat_user = st.number_input("Latitud", value=DEFAULT_LAT, format="%.6f", step=0.001)
            lon_user = st.number_input("Longitud", value=DEFAULT_LON, format="%.6f", step=0.001)
            location_label = f"{lat_user:.4f}, {lon_user:.4f}"
            location_status_text = "🗺️ Coordenadas manuales fijadas"



    # ── Render principal ──

    # ── Hero header ──
    st.markdown("""
    <div class="hero-header">
      <h1>⛽ Combustible Barato España</h1>
      <p>Encuentra las gasolineras más baratas cerca de ti · Datos oficiales del Ministerio</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Barra de estado superior ──
    loaded_at_str = loaded_at.strftime('%d/%m/%Y %H:%M')
    total_estaciones = len(df)

    st.markdown(f"""
    <div class="top-status-bar">
      <div class="top-status-item">{location_status_text}</div>
      <div class="top-status-item">📅 Datos cargados: <b>{loaded_at_str}</b></div>
      <div class="top-status-item">🏪 Total estaciones: <b>{total_estaciones:,}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Búsqueda ──
    if lat_user is None or lon_user is None:
        st.info("👈 Configura tu ubicación en la barra lateral para ver resultados.")
        return

    ordenar_por = "Precio" if "Precio" in criterio_orden else "Distancia"
    results = buscar_estaciones(df, lat_user, lon_user, radio_km, col_precio, max_res, ordenar_por)

    # ── Métricas resumen ──
    col1, col2, col3, col4 = st.columns(4)

    def metric_card(col, label, value, sub=""):
        col.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    if not results.empty:
        precio_min  = results[col_precio].min()
        precio_max  = results[col_precio].max()
        precio_med  = results[col_precio].mean()
        dist_media  = results["Distancia (km)"].mean()

        metric_card(col1, "Precio más bajo",  f"{precio_min:.3f} €/L", "🏆 El más barato")
        metric_card(col2, "Precio medio zona", f"{precio_med:.3f} €/L", "📊 Promedio")
        metric_card(col3, "Precio más alto",  f"{precio_max:.3f} €/L", "⚠️ En la zona")
        metric_card(col4, "Estaciones encontradas", str(len(results)), f"Radio: {radio_km} km")
    else:
        for c in [col1, col2, col3, col4]:
            metric_card(c, "Sin datos", "—", "")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabla de resultados ──
    if results.empty:
        st.warning(f"🚫 No se encontraron estaciones con **{combustible_nombre}** en un radio de **{radio_km} km** desde **{location_label}**.")
        st.info("💡 Prueba a ampliar el radio de búsqueda o a cambiar el tipo de combustible.")
        return

    st.markdown(f"### 🏆 Las {len(results)} gasolineras más baratas de **{combustible_nombre}** cerca de _{location_label}_")

    # Columnas a mostrar (nombres exactos en UTF-8 tal como los entrega xlrd)
    nombre_col  = next((c for c in ["Rótulo", "Nombre"] if c in results.columns), results.columns[0])
    dir_col     = next((c for c in ["Dirección", "Direccion"] if c in results.columns), None)
    muni_col    = next((c for c in ["Municipio"] if c in results.columns), None)
    prov_col    = next((c for c in ["Provincia"] if c in results.columns), None)
    horario_col = next((c for c in ["Horario"] if c in results.columns), None)

    display_cols = [nombre_col]
    if dir_col:    display_cols.append(dir_col)
    if muni_col:   display_cols.append(muni_col)
    if prov_col:   display_cols.append(prov_col)
    display_cols += [col_precio, "Distancia (km)", "📍 Maps"]
    if horario_col: display_cols.append(horario_col)

    # Asegurar que las columnas existen
    display_cols = [c for c in display_cols if c in results.columns]

    table_df = results[display_cols].copy()
    
    # Escapar campos de texto para prevenir ataques XSS a través de datos de entrada externos
    for col in [nombre_col, dir_col, muni_col, prov_col, horario_col]:
        if col and col in table_df.columns:
            table_df[col] = table_df[col].astype(str).apply(html.escape)

    table_df["Distancia (km)"] = table_df["Distancia (km)"].round(2)

    # Renombrar para la tabla
    rename_map = {col_precio: f"💶 Precio €/L", "Distancia (km)": "📡 Distancia km"}
    if nombre_col in table_df.columns:  rename_map[nombre_col] = "🏪 Gasolinera"
    if dir_col and dir_col in table_df.columns: rename_map[dir_col] = "📌 Dirección"
    if muni_col and muni_col in table_df.columns: rename_map[muni_col] = "🏘️ Municipio"
    if prov_col and prov_col in table_df.columns: rename_map[prov_col] = "🗺️ Provincia"
    if horario_col and horario_col in table_df.columns: rename_map[horario_col] = "⏰ Horario"
    table_df = table_df.rename(columns=rename_map)

    # Numerar desde 1 en lugar de 0
    table_df.index = table_df.index + 1

    # Render HTML con enlaces Maps en un contenedor con scroll horizontal
    tabla_html = table_df.to_html(escape=False, index=True, classes="results-table")
    st.markdown(
        f'<div class="table-container">{tabla_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Mapa interactivo con precios ──
    with st.expander("🗺️ Ver mapa de gasolineras", expanded=False):
        import pydeck as pdk
        
        map_df = results[["Latitud", "Longitud", col_precio, nombre_col]].copy()
        map_df = map_df.rename(columns={"Latitud": "lat", "Longitud": "lon", nombre_col: "nombre"})
        map_df["precio_str"] = map_df[col_precio].apply(lambda p: f"{p:.3f} €/L")
        
        view_state = pdk.ViewState(
            latitude=lat_user,
            longitude=lon_user,
            zoom=12,
            pitch=0,
        )
        
        scatterplot_layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position="[lon, lat]",
            get_color="[239, 68, 68, 200]",  # Rojo translúcido (#ef4444)
            get_radius=120,
            pickable=True,
        )
        
        text_layer = pdk.Layer(
            "TextLayer",
            map_df,
            get_position="[lon, lat]",
            get_text="precio_str",
            get_color="[255, 255, 255, 255]",  # Blanco
            get_size=15,
            get_alignment_baseline="'bottom'",
            get_pixel_offset="[15, -5]",  # Desplazado al lado del punto
            pickable=True,
            font_family="'Inter', sans-serif",
            font_weight="bold",
        )
        
        st.pydeck_chart(
            pdk.Deck(
                layers=[scatterplot_layer, text_layer],
                initial_view_state=view_state,
                tooltip={"html": "<b>{nombre}</b><br>Precio: {precio_str}"},
            )
        )

    # ── Footer ──
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; color:rgba(255,255,255,0.4); font-size:0.8rem; padding: 0.5rem;">
      ⛽ combustible_ybarato.es · Datos: 
      <a href="https://geoportalgasolineras.es" target="_blank" style="color:rgba(255,255,255,0.5)">
        Geoportal de Gasolineras · Ministerio para la Transición Ecológica
      </a><br>
      Actualización automática diaria a las 06:00 AM · Última actualización: {loaded_at.strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
