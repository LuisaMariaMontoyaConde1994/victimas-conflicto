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

def anchor(id_: str):
    # Inserta un ancla invisible para que <a href="#id"> salte aquí
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

# CSS para TOC fijo y scroll suave
st.markdown("""
<style>
  html { scroll-behavior: smooth; }
  .toc-box {
    position: sticky; top: 80px;
    background: rgba(255,255,255,0.9);
    border-radius: 14px; padding: 14px 14px;
    box-shadow: 0 6px 18px rgba(15,23,42,0.08);
    font-size: 0.95rem;
  }
  .toc-box a { text-decoration:none; color:#0f172a; }
  .toc-box a:hover { text-decoration:underline; }
  .toc-title { font-weight:700; margin-bottom:8px; }
  .toc-ul { list-style: none; padding-left: 0; margin: 0; }
  .toc-ul li { margin: 6px 0; }
  .toc-ul li ul { margin-top:6px; margin-left:14px; }
</style>
""", unsafe_allow_html=True)


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
<h1 style='text-align:center; font-size:2.3rem; margin-bottom:0.4em;'>
🕊️ Memoria a las  Víctimas: Víctimas del conflicto  Armado en Colombia (1950–2024)
</h1>
<p style='text-align:center; color:#374151; font-size:1.05rem; margin-top:0;'>
Datos consolidados para comprender tendencias nacionales, características de las víctimas y su situación actual.
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
  background: rgba(255,255,255,0.82);
  border-radius: 18px;
  padding: 20px 22px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.08);
  backdrop-filter: blur(4px);
  font-size: 1.05rem;
  text-align: justify;
">
<p>
Esta aplicación integra dos fuentes de información oficiales descargadas desde <strong>Datos Abiertos</strong>
(Plataforma del Gobierno de Colombia):
</p>

<ul>
  <li><strong>Base 1 (2002–2023):</strong> conjunto completo y consolidado para el análisis principal de desaparición forzada
      a nivel nacional (serie continua y homogénea).</li>
  <li><strong>Base 2 (1944–2024):</strong> <em>muestra representativa</em> utilizada de forma complementaria para aportar contexto
      histórico ampliado y contrastar patrones.</li>
</ul>

<p>
El tablero permite explorar variables sociodemográficas y territoriales para identificar patrones de género, edad,
pertenencia étnica y situación actual de las víctimas. Cada número representa una historia; el propósito es facilitar
una lectura responsable de la información, contribuir a la construcción de memoria y promover decisiones informadas.
</p>

<p style="margin-top:10px; color:#475569; font-size:0.95rem;">
<strong>Nota metodológica:</strong> los indicadores principales se presentan con la Base 1 (2002–2023).
La Base 2 se usa solo como referencia histórica agregada; por su carácter muestral no debe compararse 1:1
con las cifras consolidadas.
</p>
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

col_main, col_toc = st.columns([4, 1])  # 4/1 ó 3/1 según prefieras


st.sidebar.markdown("""
<div class="toc">
  <div style="font-weight:700; margin-bottom:6px;">📑 Secciones</div>
  <ul>
    <li>
      <details open>
        <summary><a href="#panorama" id="lnk-panorama">Panorama nacional</a></summary>
        <ul>
          <li><a href="#serie" id="lnk-serie">Serie anual</a></li>
          <li><a href="#top10" id="lnk-top10">Top 10 departamentos</a></li>
          <li><a href="#mapa" id="lnk-mapa">Mapa por departamento</a></li>
          <li><a href="#sexo" id="lnk-sexo">Distribución por sexo</a></li>
          <li><a href="#situacion" id="lnk-situacion">Situación actual</a></li>
        </ul>
      </details>
    </li>
    <details open>
        <summary><a href="#hechos" id="lnk-hechos">Otros hechos (1944–2024)</a></summary>
        <ul>
          <li><a href="#evolucion" id="lnk-evolucion">Evolución de 'Lesionados Civiles'</a></li>
          <li><a href="#hechos1" id="lnk-hechos1">Hechos más frecuentes en el período</a></li>
        </ul>
      </details>
      </li>
    <li><a href="#reflexion" id="lnk-reflexion"> Hacia la paz</a></li>
  </ul>
</div>
""", unsafe_allow_html=True)





def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("panorama")


# ========================
# Portada — narrativa y KPIs
# ========================
st.title("Panorama nacional de casos (2000–2023)")
st.caption("Fuente: dataset consolidado; esta versión usa tablas resumen para rendimiento. El rango aplica a todas las vistas.")

st.markdown("""
<div style="
  background: rgba(255,255,255,0.82);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.08);
  backdrop-filter: blur(4px);
  font-size: 1.05rem;
  text-align: justify;
">
<p>
En este apartado se presenta una visión general de los casos reportados de desaparición forzada en el periodo seleccionado.  
Los indicadores permiten identificar:
</p>
<ul>
  <li><strong>Total en rango:</strong> la suma de todos los registros en los años escogidos.</li>
  <li><strong>Año pico:</strong> el momento en el que se registró la mayor cantidad de casos.</li>
  <li><strong>Variación porcentual:</strong> la diferencia relativa entre el inicio y el final del rango de análisis.</li>
</ul>
<p>
Estos datos proporcionan un panorama inicial que ayuda a comprender la evolución del fenómeno en el tiempo 
y sirven como contexto para el resto de las visualizaciones.
</p>
</div>
""", unsafe_allow_html=True)
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

def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)
anchor("Serie")
st.header("Serie anual (nacional)")


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
def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("top10")


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
def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("mapa")


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
def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)
anchor("sexo")


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
    def anchor(id_: str):
        st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

    anchor("situacion")


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
def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("hechos")
st.header("Otros hechos (1944–2024)")

st.markdown("""
<div style="
  background: rgba(255,255,255,0.82);
  border-radius: 16px;
  padding: 20px 22px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.08);
  backdrop-filter: blur(4px);
  font-size: 1.05rem;
  text-align: justify;
">

<p>
Además del conjunto principal, se dispone de una <strong>muestra representativa</strong> que abarca el periodo 
<strong>1944–2024</strong>. Esta base no es exhaustiva, sino que fue construida como referencia histórica complementaria. 
Su valor radica en ofrecer un panorama más amplio del conflicto, permitiendo observar tendencias de largo plazo, 
identificar hitos históricos y contrastar patrones con la serie consolidada de 2002–2023.
</p>

<p>
Es importante resaltar que, por su carácter muestral, las cifras de esta base <em>no deben compararse directamente</em> 
con las del conjunto consolidado, sino entenderse como un insumo adicional que aporta contexto y profundidad 
a la memoria histórica.
</p>
</div>
""", unsafe_allow_html=True)

# 1) Carga
df2 = pd.read_csv(DATA_DIR / "datos2.csv")

# 2) Normaliza año: quitar comas internas y convertir a int
df2 = df2.rename(columns={"Año": "ANO"})
df2["ANO"] = (
    df2["ANO"]
    .astype(str)
    .str.replace(",", "", regex=False)      # "1,977" -> "1977"
    .str.strip()
)
df2["ANO"] = pd.to_numeric(df2["ANO"], errors="coerce").astype("Int64")
df2 = df2.dropna(subset=["ANO"]).copy()
df2["ANO"] = df2["ANO"].astype(int)

# 3) Columnas presentes (según diagnóstico)
flag_cols_bin = [
    "Abandono o Despojo Forzado de Tierras",
    "Amenaza o Intimidación",
    "Ataque Contra Misión Médica",
    "Confinamiento o Restricción a la Movilidad",
    "Desplazamiento Forzado",
    "Extorsión",
    "Pillaje",
]
flag_cols_bin = [c for c in flag_cols_bin if c in df2.columns]

col_lesionados = "Lesionados Civiles" if "Lesionados Civiles" in df2.columns else None
col_resp       = "Presunto Responsable" if "Presunto Responsable" in df2.columns else None
col_armas      = "Tipo de Armas" if "Tipo de Armas" in df2.columns else None
col_otros      = "Otro Hecho Simultáneo" if "Otro Hecho Simultáneo" in df2.columns else None

# 4) Selector de años usando MIN–MAX reales de esta base
all_years2 = sorted(df2["ANO"].unique().tolist())
y0, y1 = st.select_slider(
    "Rango de años (hechos)",
    options=all_years2,
    value=(min(all_years2), max(all_years2)),
    key="flt_year_range_hechos"  # independiente de tu otro selector
)

df2_f = df2[(df2["ANO"] >= y0) & (df2["ANO"] <= y1)].copy()
if df2_f.empty:
    st.info("No hay registros en el rango seleccionado.")
    st.stop()

# ========================
# 5) Gráficas
# ========================


def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("evolucion")
# 5.2 Lesionados Civiles (conteo real)
if col_lesionados:
    st.subheader("Evolución de 'Lesionados Civiles'")
    df2_f[col_lesionados] = pd.to_numeric(df2_f[col_lesionados], errors="coerce").fillna(0)
    serie_les = df2_f.groupby("ANO")[col_lesionados].sum().reset_index()
    if serie_les[col_lesionados].sum() > 0:
        fig_les = px.line(serie_les, x="ANO", y=col_lesionados, markers=True,
                          title="Total anual de lesionados civiles")
        st.plotly_chart(fig_les, use_container_width=True)
    else:
        st.info("No hay valores > 0 en 'Lesionados Civiles' para el rango.")

def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("hechos1")
# 5.3 Top modalidades (acumulado del período)
if flag_cols_bin:
    st.subheader("Hechos más frecuentes en el período")
    totales = df2_f[flag_cols_bin].sum().sort_values(ascending=False).reset_index()
    totales.columns = ["Hecho", "Casos"]
    if totales["Casos"].sum() > 0:
        fig_top = px.bar(totales.head(10), x="Casos", y="Hecho", orientation="h",
                         title="Top 10 modalidades")
        st.plotly_chart(fig_top, use_container_width=True)

# 5.4 Presuntos responsables
if col_resp:
    st.subheader("Presuntos responsables")
    resp = (df2_f[col_resp].astype(str).str.strip()
            .replace({"": None, "nan": None, "None": None})
            .dropna())
    if not resp.empty:
        resp_count = resp.value_counts().reset_index().head(10)
        resp_count.columns = ["Responsable", "Casos"]
        fig_resp = px.bar(resp_count, x="Casos", y="Responsable", orientation="h",
                          title="Top presuntos responsables")
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.info("No hay valores válidos en 'Presunto Responsable' para el rango.")



st.markdown("---")

def anchor(id_: str):
    st.markdown(f"<div id='{id_}'></div>", unsafe_allow_html=True)

anchor("reflexion")

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

# ========================
# Nueva sección: hechos victimizantes
# ========================
# ========================
# Carga robusta + diagnóstico + gráficas (datos2.csv)
# ========================
# ========================
# Sección: Otros hechos del conflicto (datos2.csv)
# ========================
# ========================
# Sección: Otros hechos del conflicto (datos2.csv) — FIX AÑO con comas
# ========================
