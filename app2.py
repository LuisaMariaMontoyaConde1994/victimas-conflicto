from pathlib import Path
import json, unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

# --- Fondo con imagen + Hero título ---
from base64 import b64encode

from pathlib import Path
DATA_DIR = Path(__file__).parent / "data"

ASSETS_DIR = DATA_DIR / "assets"    # dentro de tu carpeta data crea "assets"
BG_PATH = ASSETS_DIR / "imagen1dashboard.jpg"  # cambia el nombre si tu imagen se llama distinto



def set_background(img_path: Path):
    if not img_path.exists():
        return
    encoded = b64encode(img_path.read_bytes()).decode()
    st.markdown(f"""
    <style>
      /* Imagen de fondo con velo blanco para legibilidad */
      .stApp {{
        background: 
          linear-gradient(rgba(255,255,255,0.86), rgba(255,255,255,0.86)),
          url("data:image/jpeg;base64,{encoded}") no-repeat center fixed;
        background-size: cover;
      }}
      /* Caja del hero (título) */
      .hero {{
        padding: 28px 24px;
        border-radius: 18px;
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(4px);
        box-shadow: 0 10px 30px rgba(0,0,0,.10);
        margin: 8px 0 18px 0;
      }}
      .hero h1 {{
        margin: 0;
        font-size: 2.2rem;
        line-height: 1.2;
      }}
      .hero p {{
        margin: 6px 0 0 0;
        font-size: 1rem;
        color: #333;
      }}
    </style>
    """, unsafe_allow_html=True)

set_background(BG_PATH)

st.markdown("""
<div class="hero">
  <h1>🕊️ Memoria de las Víctimas: Desaparición Forzada en Colombia (2000–2023)</h1>
  <p>Datos consolidados para comprender tendencias nacionales, características de las víctimas y su situación actual.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="background-color: rgba(255,255,255,0.7); padding: 16px; border-radius: 12px; font-size:1.05rem; text-align:justify;">
Esta base de datos recopila y organiza los registros de desaparición en Colombia entre los años 2000 y 2023. 
Incluye variables sociodemográficas y territoriales que permiten analizar patrones de género, edad, etnia y 
situación actual de las víctimas. Su propósito es facilitar la exploración interactiva de la información 
y contribuir a la comprensión de un fenómeno que sigue marcando la historia del país.
</div>
""", unsafe_allow_html=True)



# ========================
# Configuración general
# ========================
st.set_page_config(page_title="Women DataViz — Dashboard", page_icon="📊", layout="wide")

# Cambiar color de fondo a gris y mantener colores originales de gráficos
theme_bg = "#f0f0f0"  # gris claro
text_color = "#000000"  # texto negro

st.markdown(
    f"""
    <style>
      .stApp {{background-color:{theme_bg};}}
      html, body, [class^="css"]  {{color:{text_color} !important;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================
# Utilidades
# ========================
DATA_DIR = Path(__file__).parent / "data"
PQT_RES_ANIO = DATA_DIR / "resumen_anio.parquet"
PQT_RES_ANIO_DPTO = DATA_DIR / "resumen_anio_departamento.parquet"

@st.cache_data(show_spinner=False)
def load_parquet_safe(p: Path) -> pd.DataFrame:
    return pd.read_parquet(p)

@st.cache_data(show_spinner=False)
def std_dep(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).upper().strip()
    s = s.replace(" D.C.", "").replace(" DISTRITO CAPITAL", "").replace("  ", " ")
    s = s.replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U").replace("Ñ","N")
    s = s.replace("BOGOTA,", "BOGOTA").replace("BOGOTA D C", "BOGOTA")
    s = s.replace("ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA", "SAN ANDRES")
    return s

# ========================
# Carga de data base
# ========================
if not PQT_RES_ANIO.exists():
    st.error("No encuentro data/resumen_anio.parquet")
    st.stop()

res_anio = load_parquet_safe(PQT_RES_ANIO).copy()
res_anio.rename(columns={"AÑO":"ANO", "Año":"ANO"}, inplace=True)
res_anio["ANO"] = pd.to_numeric(res_anio["ANO"], errors="coerce")
res_anio = res_anio.dropna(subset=["ANO"])
res_anio["ANO"] = res_anio["ANO"].astype(int)

PREF_MIN, PREF_MAX = 2000, 2023
res_anio = res_anio[(res_anio["ANO"] >= PREF_MIN) & (res_anio["ANO"] <= PREF_MAX)]

# ========================
# Filtro superior
# ========================
all_years = sorted(res_anio["ANO"].unique().tolist())
ymin, ymax = min(all_years), max(all_years)
sel_years = st.select_slider(
    "Rango de años",
    options=all_years,
    value=(ymin, ymax),
    key="flt_year_range"
)

res_f = res_anio[(res_anio["ANO"] >= sel_years[0]) & (res_anio["ANO"] <= sel_years[1])]

# ========================
# Portada — narrativa y KPIs
# ========================
st.title("📊 Panorama nacional de casos (2000–2023)")
st.caption("Fuente: dataset consolidado; esta versión usa tablas resumen para rendimiento. El rango aplica a todas las vistas.")

c1, c2, c3 = st.columns(3)
if not res_f.empty:
    total = int(res_f["CASOS"].sum())
    peak_row = res_f.loc[res_f["CASOS"].idxmax()]
    peak_year, peak_val = int(peak_row["ANO"]), int(peak_row["CASOS"])
    first_year = res_f.sort_values("ANO").iloc[0]
    last_year  = res_f.sort_values("ANO").iloc[-1]
    delta = ((last_year["CASOS"] - first_year["CASOS"]) / max(first_year["CASOS"],1)) * 100

    c1.metric("Total en rango", f"{total:,}".replace(",","."))
    c2.metric("Año pico", f"{peak_year}", help=f"{peak_val:,} casos".replace(",","."))
    c3.metric("Variación % (primer→último)", f"{delta:+.1f}%")
else:
    c1.metric("Total en rango", "0")
    c2.metric("Año pico", "—")
    c3.metric("Variación %", "—")

# ========================
# Serie temporal
# ========================
st.subheader("Serie anual (nacional)")
fig_line = px.line(res_f, x="ANO", y="CASOS", markers=True, title="Tendencia anual")
fig_line.update_layout(template="plotly_dark")
fig_line.update_yaxes(tickformat=",")
if not res_f.empty:
    ymax_val = int(res_f["CASOS"].max()); xmax_val = int(res_f.loc[res_f["CASOS"].idxmax(), "ANO"])
    fig_line.add_annotation(x=xmax_val, y=ymax_val, text=f"Pico: {ymax_val:,} en {xmax_val}".replace(",","."), showarrow=True, arrowhead=2)
st.plotly_chart(fig_line, use_container_width=True)



# ========================
# Top 10 departamentos
# ========================
if PQT_RES_ANIO_DPTO.exists():
    res_anio_dpto = load_parquet_safe(PQT_RES_ANIO_DPTO)
    res_anio_dpto.rename(columns={"AÑO":"ANO"}, inplace=True)
    res_anio_dpto["ANO"] = pd.to_numeric(res_anio_dpto["ANO"], errors="coerce").astype("Int64")
    res_dep = res_anio_dpto[(res_anio_dpto["ANO"] >= sel_years[0]) & (res_anio_dpto["ANO"] <= sel_years[1])].dropna(subset=["ANO"])
    top_dep = res_dep.groupby("DEPARTAMENTO", as_index=False)["CASOS"].sum().sort_values("CASOS", ascending=False).head(10)

    st.subheader("Top 10 departamentos en el rango seleccionado")
    fig_bar = px.bar(top_dep, x="DEPARTAMENTO", y="CASOS", title="Departamentos con más casos")
    fig_bar.update_layout(template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

# ========================
# Mapa por año
# ========================
if PQT_RES_ANIO_DPTO.exists():
    st.subheader("Mapa por departamento (elige un año)")
    years_map = sorted(int(y) for y in pd.to_numeric(res_anio_dpto["ANO"], errors="coerce").dropna().unique() if int(y) != 0)
    years_map = [y for y in years_map if PREF_MIN <= y <= PREF_MAX]
    year_sel = st.select_slider("Año para el mapa", options=years_map, value=years_map[-1], key="year_map")

    df_map = res_anio_dpto[res_anio_dpto["ANO"] == year_sel].groupby("DEPARTAMENTO", as_index=False)["CASOS"].sum()
    if not df_map.empty:
        df_map["DEP_STD"] = df_map["DEPARTAMENTO"].apply(std_dep)
        geo_candidates = [DATA_DIR/"geo"/"col_departamentos.geojson", DATA_DIR/"geo"/"colombia.geo.json"]
        GEO_PATH = next((p for p in geo_candidates if p.exists()), None)
        if GEO_PATH:
            with open(GEO_PATH, "r", encoding="utf-8") as f:
                gj = json.load(f)

            # 1) Detectar automáticamente la mejor propiedad del GeoJSON para unir
            props0 = gj["features"][0]["properties"]
            dep_set = set(df_map["DEP_STD"].unique())
            best_key, best_overlap = None, -1
            for k in props0.keys():
                vals = {std_dep(feat["properties"].get(k)) for feat in gj["features"]}
                overlap = len(dep_set & vals)
                if overlap > best_overlap:
                    best_key, best_overlap = k, overlap

            st.caption(f"Uniendo por `{best_key}` — coincidencias: {best_overlap} de {len(dep_set)}")

            # 2) Crear clave estandarizada dentro del GeoJSON
            for feat in gj["features"]:
                feat["properties"]["_DEP_STD"] = std_dep(feat["properties"].get(best_key))

            # 3) Dibujar el mapa (fondo claro, mismos colores de antes)
            fig_map = px.choropleth(
                df_map,
                geojson=gj,
                locations="DEP_STD",
                color="CASOS",
                featureidkey="properties._DEP_STD",
                title=f"Casos por departamento — {year_sel}",
                color_continuous_scale="Greens"
            )
            fig_map.update_geos(fitbounds="geojson", visible=False)
            fig_map.update_layout(template="plotly_white", paper_bgcolor=theme_bg, plot_bgcolor=theme_bg)
            st.plotly_chart(fig_map, use_container_width=True)

# ========================
# Auditoría de datos
# ========================
with st.expander("🔍 Auditoría — ¿qué datos está usando la app ahora?"):
    st.write("Dimensión resumen (años):", res_anio.shape)
    st.write("Rango seleccionado:", sel_years)
    st.write("Conteo por año (filtrado):")
    st.dataframe(res_f.groupby("ANO", as_index=False)["CASOS"].sum())
    st.write("Primeras filas del resumen:")
    st.dataframe(res_anio.head(10))
    if PQT_RES_ANIO_DPTO.exists():
        st.write("Ejemplo año seleccionado para mapa (top 10):")
        st.dataframe(df_map.sort_values("CASOS", ascending=False).head(10))

# ========================
# Sexo: carga y gráficas
# ========================
PQT_SEXO = DATA_DIR / "resumen_dep_estado_sexo.parquet"
if PQT_SEXO.exists():
    sexo = load_parquet_safe(PQT_SEXO).copy()
    for c_old in ["AÑO","Año"]:
        if c_old in sexo.columns:
            sexo.rename(columns={c_old:"ANO"}, inplace=True)
    sexo["ANO"] = pd.to_numeric(sexo["ANO"], errors="coerce").fillna(0).astype(int)
    sexo = sexo[sexo["ANO"] > 0]

    sexo_f = sexo[(sexo["ANO"] >= sel_years[0]) & (sexo["ANO"] <= sel_years[1])]
    if sexo_f.empty:
        st.warning("No hay datos de sexo en el rango seleccionado.")
    else:
        st.subheader("Distribución por sexo")
        include_unknown = st.checkbox("Incluir 'SIN INFORMACION'", value=False, key="sex_unknown")
        if not include_unknown:
            sexo_f = sexo_f[sexo_f["Sexo"].str.upper() != "SIN INFORMACION"]

        # Pie chart
        tot_sexo = sexo_f.groupby("Sexo", as_index=False)["CASOS"].sum()
        st.plotly_chart(
            px.pie(tot_sexo, values="CASOS", names="Sexo", title="Proporción por sexo"),
            use_container_width=True
        )
        # Consolidar nacional: casos por año y sexo
        serie_sexo = sexo_f.groupby(["ANO", "Sexo"], as_index=False)["CASOS"].sum()

        fig_line_sexo = px.line(
            serie_sexo, x="ANO", y="CASOS", color="Sexo", markers=True,
            title="Tendencia nacional por sexo"
        )
        fig_line_sexo.update_layout(template="plotly_dark")
        st.plotly_chart(fig_line_sexo, use_container_width=True)
    # ========================
    # Situación actual de la víctima
    # ========================
    PQT_SIT = DATA_DIR / "resumen_dep_estado_situacion.parquet"
    if PQT_SIT.exists():
        sit = load_parquet_safe(PQT_SIT).copy()
        for c_old in ["AÑO", "Año"]:
            if c_old in sit.columns:
                sit.rename(columns={c_old: "ANO"}, inplace=True)
        sit["ANO"] = pd.to_numeric(sit["ANO"], errors="coerce").fillna(0).astype(int)
        sit = sit[sit["ANO"] > 0]

        sit_f = sit[(sit["ANO"] >= sel_years[0]) & (sit["ANO"] <= sel_years[1])]

        if sit_f.empty:
            st.warning("No hay datos de situación actual en este rango.")
        else:
            st.subheader("Situación actual de la víctima")

            # Total nacional por situación en el rango
            tot_sit = sit_f.groupby("SITUACION", as_index=False)["CASOS"].sum()

            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(tot_sit, values="CASOS", names="SITUACION",
                                 title="Proporción en el rango")
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                serie_sit = sit_f.groupby(["ANO", "SITUACION"], as_index=False)["CASOS"].sum()
                fig_line = px.line(serie_sit, x="ANO", y="CASOS", color="SITUACION", markers=True,
                                   title="Evolución anual por situación")
                st.plotly_chart(fig_line, use_container_width=True)
st.markdown("---")

st.header("🕊️ Un camino hacia la paz")

st.markdown("""
<div style="background-color: rgba(255,255,255,0.75); padding: 22px; 
            border-radius: 12px; font-size:1.1rem; text-align:justify; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
<p><em>"La paz no es solo la ausencia de guerra, sino también una cultura de paz 
que se construye a través de la educación y el cambio social."</em></p>

<p>El análisis de estos datos nos recuerda que cada número corresponde a una vida, 
a una historia y a una familia. Conocer, estudiar y visibilizar estas cifras es 
fundamental para comprender la magnitud de la violencia que ha marcado nuestra 
historia reciente y, al mismo tiempo, para construir memoria y avanzar hacia 
una sociedad más justa y en paz.</p>
</div>
""", unsafe_allow_html=True)





