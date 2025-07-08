import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# Konfigurasi halaman
st.set_page_config(page_title="Peta Jaringan Alat Pengamatan Iklim", layout="wide")
st.title("🛰️ Peta Jaringan Alat Pengamatan Iklim di Indonesia")

# Warna dan simbol per jenis alat
warna_jenis = {
    "AAWS": ("purple", "cloud"),
    "AWS": ("green", "info-sign"),
    "ARG": ("blue", "tint"),
    "IKRO": ("orange", "leaf"),
    "ASRS": ("red", "fire")
}

# Folder data
data_folder = "data_xls"
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

# Gabungkan semua CSV jadi satu DataFrame
df_list = []
for file in csv_files:
    df = pd.read_csv(os.path.join(data_folder, file), encoding='utf-8', sep=';')
    if "jenis_alat" not in df.columns:
        jenis_alat = file.replace("Metadata ", "").replace(".csv", "").upper()
        df["jenis_alat"] = jenis_alat
    df_list.append(df)
df_all = pd.concat(df_list, ignore_index=True)

# --- Filter Sidebar ---
st.sidebar.header("🔎 Filter Peta")
daftar_provinsi = sorted(df_all['nama_propinsi'].dropna().unique())
daftar_alat = sorted(df_all['jenis_alat'].dropna().unique())

# Dropdown filter
filter_provinsi = st.sidebar.selectbox("Pilih Provinsi", options=["Semua Provinsi"] + daftar_provinsi)
filter_alat = st.sidebar.selectbox("Pilih Jenis Alat", options=["Semua Jenis Alat"] + daftar_alat)

# Terapkan filter
df_filtered = df_all.copy()
if filter_provinsi != "Semua Provinsi":
    df_filtered = df_filtered[df_filtered["nama_propinsi"] == filter_provinsi]
if filter_alat != "Semua Jenis Alat":
    df_filtered = df_filtered[df_filtered["jenis_alat"] == filter_alat]

# Buat peta Indonesia
m = folium.Map(location=[-2.5, 118], zoom_start=5)

# Tambahkan marker ke peta
cluster = MarkerCluster().add_to(m)
for _, row in df_filtered.iterrows():
    alat = row['jenis_alat']
    prov = row['nama_propinsi']
    lat = row['latt_station']
    lon = row['long_station']
    nama = row['name_station']

    color, icon = warna_jenis.get(alat, ("gray", "question-sign"))
    popup_info = f"""
    <b>Nama:</b> {nama}<br>
    <b>Provinsi:</b> {prov}<br>
    <b>Jenis Alat:</b> {alat}<br>
    <b>Status:</b> {row.get('status_operasional', '-') }<br>
    <b>Instansi:</b> {row.get('instansi', '-') }
    """

    folium.Marker(
        location=[lat, lon],
        popup=popup_info,
        icon=folium.Icon(color=color, icon=icon, prefix="glyphicon")
    ).add_to(cluster)

# Tampilkan peta
st.subheader("🗺️ Peta Lokasi Alat Pengamatan")
st_folium(m, width=1000, height=600)

# --- Ringkasan Data ---
st.subheader("📊 Ringkasan Jumlah Alat")
summary = df_all.groupby(['nama_propinsi', 'jenis_alat']).size().reset_index(name='Jumlah')
total_summary = df_all['jenis_alat'].value_counts().reset_index()
total_summary.columns = ['Jenis Alat', 'Jumlah Total']

# Tampilkan tabel
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔢 Per Provinsi & Jenis Alat")
    st.dataframe(summary)

with col2:
    st.markdown("### 🔢 Total Keseluruhan")
    st.dataframe(total_summary)

# --- Unduh PDF ---
st.subheader("📁 Unduhan File PDF Metadata")
pdf_folder = "file_peta"
if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith(".pdf")])
    selected_pdf = st.selectbox("Pilih file PDF untuk diunduh:", pdf_files)
    with open(os.path.join(pdf_folder, selected_pdf), "rb") as f:
        st.download_button(label="📥 Unduh PDF", data=f, file_name=selected_pdf, mime="application/pdf")
else:
    st.info("Folder PDF belum ditemukan atau kosong.")
