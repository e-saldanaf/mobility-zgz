import streamlit as st
import pydeck as pdk
import pandas as pd
import requests

# ── Page config ──────────────────────────────────────────────────────────────
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

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_stations() -> pd.DataFrame:
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()

        data = response.json()
        stations = data.get("result", []) if isinstance(data, dict) else data

        rows = []
        for item in stations:
            coords = item.get("geometry", {}).get("coordinates", [0, 0])
            rows.append({
                "id":        item.get("id"),
                "name":      item.get("title", "Unknown"),
                "bikes":     int(item.get("bicisDisponibles") or 0),
                "docks":     int(item.get("anclajesDisponibles") or 0),
                "lon":       float(coords[0]) if coords else 0.0,
                "lat":       float(coords[1]) if coords else 0.0,
                "updated":   item.get("lastUpdated", ""),
            })

        df = pd.DataFrame(rows)
        df = df[(df["lat"] != 0) & (df["lon"] != 0)]
        df["total"] = df["bikes"] + df["docks"]
        df["availability"] = (df["bikes"] / df["total"].replace(0, 1) * 100).round(1)
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


# ── Color helper ──────────────────────────────────────────────────────────────
def availability_color(pct: float) -> list[int]:
    """Green → Yellow → Red based on bike availability."""
    if pct >= 60:
        return [34, 197, 94, 200]    # green
    elif pct >= 30:
        return [250, 204, 21, 200]   # yellow
    else:
        return [239, 68, 68, 200]    # red


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🚲 Bizi Zaragoza — Live Station Map")
st.caption("Real-time availability of public bike stations in Zaragoza. Data from [Zaragoza Open Data](https://www.zaragoza.es/sede/portal/datos-abiertos/).")

# Refresh button
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

df = fetch_stations()

if df.empty:
    st.warning("No station data available. Please try again later.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────
total_bikes  = df["bikes"].sum()
total_docks  = df["docks"].sum()
total_stations = len(df)
active_stations = len(df[df["bikes"] > 0])

k1, k2, k3, k4 = st.columns(4)
k1.metric("🚲 Available Bikes",  total_bikes)
k2.metric("🅿️ Available Docks",  total_docks)
k3.metric("📍 Total Stations",   total_stations)
k4.metric("✅ Active Stations",  active_stations)

st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    min_bikes = st.slider("Minimum bikes available", 0, 20, 0)
    show_empty = st.checkbox("Show empty stations", value=True)

    st.markdown("---")
    st.markdown("**Color legend**")
    st.markdown("🟢 ≥ 60% availability")
    st.markdown("🟡 30–60% availability")
    st.markdown("🔴 < 30% availability")

# Apply filters
filtered = df[df["bikes"] >= min_bikes]
if not show_empty:
    filtered = filtered[filtered["bikes"] > 0]

# ── Map ───────────────────────────────────────────────────────────────────────
filtered["color"] = filtered["availability"].apply(availability_color)
filtered["radius"] = 30 + (filtered["bikes"] * 3).clip(upper=80)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True,
    radius_min_pixels=6,
    radius_max_pixels=30,
)

view_state = pdk.ViewState(
    latitude=41.6488,
    longitude=-0.8891,
    zoom=13,
    pitch=30,
)

tooltip = {
    "html": """
        <b>🚲 {name}</b><br/>
        Bikes available: <b>{bikes}</b><br/>
        Docks available: <b>{docks}</b><br/>
        Availability: <b>{availability}%</b>
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
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    ),
    use_container_width=True,
    height=520,
)

# ── Station table ─────────────────────────────────────────────────────────────
st.subheader("Station Details")

display_df = (
    filtered[["name", "bikes", "docks", "availability", "updated"]]
    .sort_values("bikes", ascending=False)
    .reset_index(drop=True)
)
display_df.columns = ["Station", "Bikes", "Docks", "Availability (%)", "Last Updated"]

st.dataframe(display_df, use_container_width=True, hide_index=True)