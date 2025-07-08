import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# Konfigurasi halaman
st.set_page_config(page_title="Peta Jaringan Alat Pengamatan Iklim", layout="wide")
st.title("🗺️ Peta Jaringan Alat Pengamatan Iklim")

# Warna alat
warna_jenis = {
    "AAWS": "red",
    "AWS": "blue",
    "ARG": "green",
    "IKRO": "orange",
    "ASRS": "purple"
}

# Folder data
data_folder = "data_xls"
pdf_folder = "file_peta"

# Gabungkan semua CSV jadi satu DataFrame
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
df_all = pd.DataFrame()

for file in csv_files:
    df = pd.read_csv(os.path.join(data_folder, file), encoding='utf-8', sep=';')

    if "jenis_alat" not in df.columns:
        jenis = file.replace("Metadata ", "").replace(".csv", "").upper()
        df["jenis_alat"] = jenis
    df_all = pd.concat([df_all, df], ignore_index=True)

# Dropdown Filter Provinsi
list_provinsi = sorted(df_all['nama_propinsi'].dropna().unique())
provinsi_dipilih = st.selectbox("🌍 Pilih Provinsi:", options=["Semua Provinsi"] + list_provinsi, index=0)

# Dropdown Filter Jenis Alat
list_alat = sorted(df_all['jenis_alat'].dropna().unique())
alat_dipilih = st.selectbox("🛰️ Pilih Jenis Alat:", options=["Semua Alat"] + list_alat, index=0)

# Filter DataFrame
df_filtered = df_all.copy()
if provinsi_dipilih != "Semua Provinsi":
    df_filtered = df_filtered[df_filtered['nama_propinsi'] == provinsi_dipilih]
if alat_dipilih != "Semua Alat":
    df_filtered = df_filtered[df_filtered['jenis_alat'] == alat_dipilih]

# Buat peta
m = folium.Map(location=[-2.5, 118], zoom_start=5)

provinsi_cluster = {}

for _, row in df_filtered.iterrows():
    alat_nama = row['name_station']
    provinsi = row['nama_propinsi']
    lat = row['latt_station']
    lon = row['long_station']
    jenis_alat = row['jenis_alat']

    if provinsi not in provinsi_cluster:
        provinsi_cluster[provinsi] = MarkerCluster(name=provinsi).add_to(m)

    popup = f"""
    <b>Nama:</b> {alat_nama}<br>
    <b>Jenis:</b> {jenis_alat}<br>
    <b>Provinsi:</b> {provinsi}<br>
    <b>Status:</b> {row.get('status_operasional', 'Tidak Ada Info')}<br>
    <b>Instansi:</b> {row.get('instansi', 'Tidak Ada Info')}
    """

    folium.Marker(
        location=[lat, lon],
        popup=popup,
        icon=folium.Icon(color=warna_jenis.get(jenis_alat, 'gray'))
    ).add_to(provinsi_cluster[provinsi])

# Tampilkan peta
st_data = st_folium(m, width=1000, height=600)

# Dropdown untuk download PDF
st.subheader("📄 Download Dokumen PDF Alat Pengamatan")

if os.path.exists(pdf_folder):
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith(".pdf")])
    if pdf_files:
        selected_pdf = st.selectbox("📥 Pilih File PDF untuk Diunduh:", ["Pilih file..."] + pdf_files)
        if selected_pdf != "Pilih file...":
            with open(os.path.join(pdf_folder, selected_pdf), "rb") as file:
                st.download_button(
                    label=f"Unduh {selected_pdf}",
                    data=file,
                    file_name=selected_pdf,
                    mime="application/pdf"
                )
    else:
        st.info("Tidak ada file PDF ditemukan.")
else:
    st.warning("Folder file_peta tidak ditemukan.")
