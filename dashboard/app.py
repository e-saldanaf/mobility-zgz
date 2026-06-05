import streamlit as st
import pydeck as pdk
import pandas as pd
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bizi Zaragoza — Live Map",
    page_icon="🚲",
    layout="wide",
)

# ── Constants ─────────────────────────────────────────────────────────────────
API_URL = (
    "https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/"
    "estacion-bicicleta.json?rf=json&start=0&rows=1000"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
}

# ── Color helpers ─────────────────────────────────────────────────────────────
def count_to_color(value: int, capacity: int) -> list[int]:
    if capacity == 0:
        return [100, 100, 100, 180]
    ratio = value / capacity
    if ratio >= 0.6:   return [34,  197, 94,  230]
    elif ratio >= 0.35: return [250, 204, 21,  230]
    elif ratio >= 0.1:  return [249, 115, 22,  230]
    elif value > 0:     return [220, 38,  38,  230]
    else:               return [127, 29,  29,  230]

def ratio_to_bar_color(ratio: float) -> str:
    if ratio >= 0.6:   return "#22C55E"
    elif ratio >= 0.35: return "#FACC15"
    elif ratio >= 0.1:  return "#F97316"
    elif ratio > 0:     return "#DC2626"
    else:               return "#7F1D1D"

def semaforo_estado(bikes: int, slots: int) -> str:
    if bikes == 0:  return "CRÍTICO: Vacía"
    if slots == 0:  return "CRÍTICO: Llena"
    if bikes <= 2:  return "Advertencia: Casi vacía"
    if slots <= 2:  return "Advertencia: Casi llena"
    return "Normal"

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_stations() -> pd.DataFrame:
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
        stations = data.get("result", []) if isinstance(data, dict) else data

        rows = []
        for item in stations:
            coords = item.get("geometry", {}).get("coordinates", [0, 0])
            title  = item.get("title", "") or ""
            parts  = title.split("-", 1)
            numero = parts[0].strip() if parts else ""
            nombre = parts[1].strip() if len(parts) > 1 else title
            bikes  = int(item.get("bicisDisponibles") or 0)
            slots  = int(item.get("anclajesDisponibles") or 0)
            total  = bikes + slots

            rows.append({
                "id":                    item.get("id"),
                "numero_estacion":       numero,
                "nombre_estacion":       nombre,
                "bicis_disponibles":     bikes,
                "huecos_libres":         slots,
                "capacidad_total":       total,
                "porcentaje_ocupacion":  round(bikes / total * 100, 2) if total > 0 else 0.0,
                "semaforo_estado":       semaforo_estado(bikes, slots),
                "ultima_actualizacion":  item.get("lastUpdated", ""),
                "lon":                   float(coords[0]) if coords else 0.0,
                "lat":                   float(coords[1]) if coords else 0.0,
            })

        df = pd.DataFrame(rows)
        df = df[(df["lat"] != 0) & (df["lon"] != 0)]
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🚲 Bizi Zaragoza — Live Station Map")
st.caption(
    "Disponibilidad en tiempo real de las estaciones Bizi de Zaragoza. "
    "Datos: [Zaragoza Open Data](https://www.zaragoza.es/sede/portal/datos-abiertos/)."
)

col_btn, _ = st.columns([1, 6])
with col_btn:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

df = fetch_stations()
if df.empty:
    st.warning("No hay datos disponibles. Inténtalo de nuevo más tarde.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🚲 Bicis disponibles",   int(df["bicis_disponibles"].sum()))
k2.metric("🅿️ Huecos libres",       int(df["huecos_libres"].sum()))
k3.metric("📍 Total estaciones",    len(df))
k4.metric("✅ Estaciones activas",  int((df["bicis_disponibles"] > 0).sum()))
k5.metric("🔴 Estaciones críticas", int(df["semaforo_estado"].str.startswith("CRÍTICO").sum()))

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Modo de visualización")
    modo = st.radio(
        "¿Qué quieres hacer?",
        options=["🚲 Coger una bizi", "🅿️ Dejar una bizi"],
        index=0,
    )

    st.markdown("---")
    st.header("Filtros")
    show_empty = st.checkbox("Mostrar estaciones vacías/llenas", value=True)
    min_value  = st.slider(
        "Mínimo disponible" if modo == "🚲 Coger una bizi" else "Mínimo huecos",
        0, 20, 0
    )

    st.markdown("---")
    st.markdown("**Leyenda**")
    for color, label in [
        ("#22C55E", "Alta disponibilidad (≥ 60%)"),
        ("#FACC15", "Disponibilidad media (35–60%)"),
        ("#F97316", "Disponibilidad baja (10–35%)"),
        ("#DC2626", "Casi agotado (< 10%)"),
        ("#7F1D1D", "Sin disponibilidad"),
    ]:
        st.markdown(
            f'<span style="display:inline-block;width:14px;height:14px;border-radius:50%;'
            f'background:{color};margin-right:8px;vertical-align:middle;"></span>{label}',
            unsafe_allow_html=True,
        )

# ── Filters & colors ──────────────────────────────────────────────────────────
coger_bizi = modo == "🚲 Coger una bizi"
value_col  = "bicis_disponibles" if coger_bizi else "huecos_libres"

filtered = df[df[value_col] >= min_value].copy()
if not show_empty:
    filtered = filtered[filtered[value_col] > 0]

filtered["color"]  = filtered.apply(
    lambda r: count_to_color(r[value_col], r["capacidad_total"]), axis=1
)
filtered["radius"] = (30 + filtered[value_col] * 3).clip(upper=90).astype(int)

# ── Map ───────────────────────────────────────────────────────────────────────
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True,
    radius_min_pixels=5,
    radius_max_pixels=28,
)

tooltip = {
    "html": """
        <b>{nombre_estacion}</b><br/>
        Estación nº {numero_estacion}<br/>
        🚲 Bicis: <b>{bicis_disponibles}</b> &nbsp;|&nbsp;
        🅿️ Huecos: <b>{huecos_libres}</b><br/>
        Capacidad: {capacidad_total} &nbsp;|&nbsp;
        Ocupación: <b>{porcentaje_ocupacion}%</b><br/>
        Estado: <b>{semaforo_estado}</b>
    """,
    "style": {
        "backgroundColor": "#1a1a2e",
        "color": "#FFD43B",
        "fontSize": "13px",
        "padding": "10px",
        "borderRadius": "8px",
    },
}

st.pydeck_chart(
    pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=pdk.ViewState(
            latitude=41.6488, longitude=-0.8891, zoom=13, pitch=30
        ),
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    ),
    use_container_width=True,
    height=520,
)

# ── Table with progress bars ──────────────────────────────────────────────────
st.subheader("Detalle de Estaciones")

display_df = filtered[[
    "numero_estacion", "nombre_estacion",
    "bicis_disponibles", "huecos_libres",
    "capacidad_total", "porcentaje_ocupacion",
    "ultima_actualizacion"
]].copy()

display_df["_num_sort"] = pd.to_numeric(display_df["numero_estacion"], errors="coerce")
display_df = display_df.sort_values("_num_sort").drop(columns="_num_sort").reset_index(drop=True)

# Build HTML progress bar column
def make_bar(pct: float) -> str:
    color = ratio_to_bar_color(pct / 100)
    width = max(2, int(pct))
    return (
        f'<div style="background:#1e1e2e;border-radius:4px;height:18px;width:100%;">'
        f'<div style="background:{color};width:{width}%;height:100%;border-radius:4px;'
        f'display:flex;align-items:center;justify-content:flex-end;padding-right:4px;">'
        f'<span style="color:white;font-size:10px;font-weight:bold;">{pct:.1f}%</span>'
        f'</div></div>'
    )

display_df["Bicis (%)"] = display_df["porcentaje_ocupacion"].apply(make_bar)

display_df = display_df.rename(columns={
    "numero_estacion":      "Nº",
    "nombre_estacion":      "Estación",
    "bicis_disponibles":    "Bicis",
    "huecos_libres":        "Huecos",
    "capacidad_total":      "Capacidad",
    "ultima_actualizacion": "Últ. actualización",
})

display_df = display_df[["Nº", "Estación", "Bicis", "Huecos", "Capacidad", "Bicis (%)", "Últ. actualización"]]

st.write(
    display_df.to_html(escape=False, index=False),
    unsafe_allow_html=True,
)