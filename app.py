import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import folium
from streamlit_folium import st_folium
from modules.style import load_css

# ==========================
# Konfigurasi Halaman
# ==========================
st.set_page_config(
    page_title="Dashboard Pemupukan",
    page_icon="🌴",
    layout="wide"
)
load_css()

# ==========================
# Membaca Data
# ==========================
df = pd.read_csv("data/data_pemupukan.CSV")
df["Tanggal"] = pd.to_datetime(
    df["Tanggal"],
    dayfirst=True,
    format="mixed"
)
# ==========================
# Sidebar Filter
# ==========================

st.sidebar.header("🔎 Filter Data")
# ==========================
# FILTER TANGGAL
# ==========================

tanggal = st.sidebar.date_input(
    "📅 Pilih Rentang Tanggal",
    value=(
        df["Tanggal"].min(),
        df["Tanggal"].max()
    )
)

unit = st.sidebar.selectbox(
    "Pilih Unit",
    ["Semua"] + sorted(df["Unit"].unique())
)

blok = st.sidebar.selectbox(
    "📍 Blok",
    ["Semua"] + sorted(df["Blok"].unique())
)

jenis = st.sidebar.selectbox(
    "Jenis Pupuk",
    ["Semua"] + sorted(df["Jenis Pupuk"].unique().tolist())
)

metode = st.sidebar.selectbox(
    "Metode Aplikasi",
    ["Semua"] + sorted(df["Metode"].unique().tolist())
)
# ==========================
# Proses Filter
# ==========================

df_filter = df.copy()
# Filter tanggal
if len(tanggal) == 2:
    awal, akhir = tanggal

    df_filter = df_filter[
        (df_filter["Tanggal"] >= pd.to_datetime(awal))
        &
        (df_filter["Tanggal"] <= pd.to_datetime(akhir))
    ]

if unit != "Semua":
    df_filter = df_filter[df_filter["Unit"] == unit]
    
if blok != "Semua":
    df_filter = df_filter[
        df_filter["Blok"] == blok
    ]
    
if jenis != "Semua":
    df_filter = df_filter[df_filter["Jenis Pupuk"] == jenis]

if metode != "Semua":
    df_filter = df_filter[df_filter["Metode"] == metode]

# ==========================
# Header
# ==========================
st.title("🌴 Dashboard Pemupukan Kelapa Sawit")
st.caption("Monitoring Aplikasi Pemupukan")

st.divider()

# ==========================
# KPI
# ==========================
total_pupuk = df_filter["Jumlah (Kg)"].sum()
total_hk = df_filter["HK"].sum()
total_unit = df_filter["Unit"].nunique()
total_blok = df_filter["Blok"].nunique()
jenis_pupuk = df_filter["Jenis Pupuk"].nunique()
rata_pupuk = round(
    df_filter["Jumlah (Kg)"].mean(),
    2
)
col1, col2, col3, col4 = st.columns(4)

col1.metric("🌾 Total Pupuk", f"{total_pupuk:,.0f} Kg")
col2.metric("👷 Total HK", f"{total_hk}")
col3.metric("🌴 Total Unit", total_unit)
col4.metric("🧪 Jenis Pupuk", jenis_pupuk)

st.divider()
st.subheader("📊 Analisis Pemupukan")

col1, col2 = st.columns(2)
grafik_unit = (
    df_filter.groupby("Unit")["Jumlah (Kg)"]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    grafik_unit,
    x="Unit",
    y="Jumlah (Kg)",
    title="Total Pupuk per Unit",
    text_auto=True
)

col1.plotly_chart(fig_bar, use_container_width=True)
grafik_jenis = (
    df_filter.groupby("Jenis Pupuk")["Jumlah (Kg)"]
    .sum()
    .reset_index()
)

fig_pie = px.pie(
    grafik_jenis,
    names="Jenis Pupuk",
    values="Jumlah (Kg)",
    title="Distribusi Jenis Pupuk"
)

col2.plotly_chart(fig_pie, use_container_width=True)
st.subheader("📈 Tren Pemupukan")

tren = (
    df_filter.groupby("Tanggal")["Jumlah (Kg)"]
    .sum()
    .reset_index()
)

fig_line = px.line(
    tren,
    x="Tanggal",
    y="Jumlah (Kg)",
    markers=True,
    title="Tren Jumlah Pupuk per Tanggal"
)

st.plotly_chart(fig_line, use_container_width=True)
st.subheader("🗺️ Peta Aplikasi Pemupukan")

# Titik tengah peta
lat = df_filter["Latitude"].mean()
lon = df_filter["Longitude"].mean()

m = folium.Map(
    location=[lat, lon],
    zoom_start=12
)

# Marker setiap blok
for _, row in df_filter.iterrows():

    folium.Marker(
        [row["Latitude"], row["Longitude"]],
        popup=f"""
        <b>Unit :</b> {row['Unit']}<br>
        <b>Blok :</b> {row['Blok']}<br>
        <b>Pupuk :</b> {row['Jenis Pupuk']}<br>
        <b>Jumlah :</b> {row['Jumlah (Kg)']} Kg<br>
        <b>HK :</b> {row['HK']}
        """
    ).add_to(m)

st_folium(m, width=1200, height=500)

buffer = BytesIO()

with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_filter.to_excel(
        writer,
        index=False,
        sheet_name="Pemupukan"
    )

st.download_button(
    label="📥 Download Data Excel",
    data=buffer.getvalue(),
    file_name="hasil_pemupukan.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
st.subheader("📋 Data Pemupukan")

st.dataframe(df_filter, use_container_width=True)