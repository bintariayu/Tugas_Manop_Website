import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# Judul halaman
st.set_page_config(page_title="Peta Jaringan Alat Pengamatan Iklim", layout="wide")
st.title("🗺️ Peta Jaringan Alat Pengamatan Iklim")

# Baca semua file .csv
data_folder = "data_xls"
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
warna_alat = ['red', 'blue', 'green', 'orange', 'purple']  # 1 warna per alat

# Buat peta kosong
m = folium.Map(location=[-2.5, 118], zoom_start=5)  # Pusat Indonesia
provinsi_cluster = {}

for i, file in enumerate(csv_files):
    df = pd.read_csv(os.path.join(data_folder, file), encoding='utf-8', sep=';')
    alat_nama = df['name_station'].iloc[0]
    provinsi = df['nama_propinsi'].iloc[0]
    lat = df['latt_station'].iloc[0]
    lon = df['long_station'].iloc[0]

    # Buat kluster berdasarkan provinsi
    if provinsi not in provinsi_cluster:
        provinsi_cluster[provinsi] = MarkerCluster(name=provinsi).add_to(m)

    # Tambahkan marker
    folium.Marker(
        location=[lat, lon],
        popup=f"{alat_nama} ({provinsi})",
        icon=folium.Icon(color=warna_alat[i])
    ).add_to(provinsi_cluster[provinsi])

# Tampilkan peta
st_data = st_folium(m, width=900, height=600)

# Unduh PDF
st.subheader("📄 Download PDF Alat Pengamatan")
pdf_folder = "file_peta"
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
for pdf in pdf_files:
    with open(os.path.join(pdf_folder, pdf), "rb") as f:
        st.download_button(label=f"Unduh {pdf}", data=f, file_name=pdf)
