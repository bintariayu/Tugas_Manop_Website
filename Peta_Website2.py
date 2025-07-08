import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# Judul halaman
st.set_page_config(page_title="Peta Jaringan Alat Pengamatan Iklim", layout="wide")
st.title("🗺️ Peta Jaringan Alat Pengamatan Iklim")

# Warna untuk tiap jenis alat
warna_jenis = {
    "AAWS": "red",
    "AWS": "blue",
    "ARG": "green",
    "IKRO": "orange",
    "ASRS": "purple"
}

# Folder data
data_folder = "data_xls"
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

# Buat peta dasar
m = folium.Map(location=[-2.5, 118], zoom_start=5)

# Klaster per provinsi
provinsi_cluster = {}

# Loop semua file CSV
for file in csv_files:
    df = pd.read_csv(os.path.join(data_folder, file), encoding='utf-8', sep=';')

    if "jenis_alat" not in df.columns:
        # Deteksi jenis alat dari nama file jika tidak ada di kolom
        jenis_alat = file.replace("Metadata ", "").replace(".csv", "").upper()
        df["jenis_alat"] = jenis_alat
    else:
        jenis_alat = df["jenis_alat"].iloc[0]

    for _, row in df.iterrows():
        alat_nama = row['name_station']
        provinsi = row['nama_propinsi']
        lat = row['latt_station']
        lon = row['long_station']

        # Buat cluster per provinsi
        if provinsi not in provinsi_cluster:
            provinsi_cluster[provinsi] = MarkerCluster(name=provinsi).add_to(m)

        # Popup info alat
        popup = f"""
        <b>Nama:</b> {alat_nama}<br>
        <b>Jenis:</b> {jenis_alat}<br>
        <b>Provinsi:</b> {provinsi}<br>
        <b>Status:</b> {row.get('status_operasional', 'Tidak Ada Info')}<br>
        <b>Instansi:</b> {row.get('instansi', 'Tidak Ada Info')}
        """

        # Tambahkan marker
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            icon=folium.Icon(color=warna_jenis.get(jenis_alat, 'gray'))
        ).add_to(provinsi_cluster[provinsi])

# Tampilkan peta
st_data = st_folium(m, width=1000, height=600)

# Unduh PDF
st.subheader("📄 Download PDF Alat Pengamatan")
pdf_folder = "file_peta"
if os.path.exists(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    for pdf in pdf_files:
        with open(os.path.join(pdf_folder, pdf), "rb") as f:
            st.download_button(label=f"📥 Unduh {pdf}", data=f, file_name=pdf, mime="application/pdf")
