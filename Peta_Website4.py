import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# ------------------- Konfigurasi -------------------
st.set_page_config(page_title="Peta Alat Pengamatan Iklim", layout="wide")
st.title("🛰️ Peta Interaktif Jaringan Alat Pengamatan Iklim")

# Warna dan simbol khusus untuk tiap jenis alat
alat_styling = {
    "AAWS": {"color": "red", "icon": "cloud"},
    "AWS": {"color": "blue", "icon": "info-sign"},
    "ARG": {"color": "green", "icon": "tint"},
    "IKRO": {"color": "orange", "icon": "sun"},
    "ASRS": {"color": "purple", "icon": "star"},
}

# Folder data
csv_folder = "data_xls"
pdf_folder = "file_peta"
csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]

# ------------------- Load & Gabungkan Data -------------------
df_all = pd.DataFrame()

for file in csv_files:
    df = pd.read_csv(os.path.join(csv_folder, file), encoding='utf-8', sep=';')

    if "jenis_alat" not in df.columns:
        alat_jenis = file.replace("Metadata ", "").replace(".csv", "").upper()
        df["jenis_alat"] = alat_jenis
    df["nama_file"] = file.replace(".csv", "")
    df_all = pd.concat([df_all, df], ignore_index=True)

# ------------------- Filter Sidebar -------------------
prov_list = sorted(df_all['nama_propinsi'].dropna().unique())
alat_list = sorted(df_all['jenis_alat'].dropna().unique())

# Filter Provinsi
provinsi_terpilih = st.sidebar.selectbox("📍 Pilih Provinsi", ["Seluruh Indonesia"] + prov_list)

# Filter Jenis Alat
alat_terpilih = st.sidebar.multiselect("🔧 Pilih Jenis Alat", alat_list, default=alat_list)

# ------------------- Filter Data -------------------
df_filtered = df_all[df_all["jenis_alat"].isin(alat_terpilih)]
if provinsi_terpilih != "Seluruh Indonesia":
    df_filtered = df_filtered[df_filtered["nama_propinsi"] == provinsi_terpilih]

# ------------------- Buat Peta -------------------
m = folium.Map(location=[-2.5, 118], zoom_start=5 if provinsi_terpilih == "Seluruh Indonesia" else 7)
prov_cluster = MarkerCluster(name="Cluster").add_to(m)

for _, row in df_filtered.iterrows():
    lat, lon = row['latt_station'], row['long_station']
    alat = row['jenis_alat']
    warna = alat_styling.get(alat, {"color": "gray", "icon": "info-sign"})

    popup = f"""
    <b>Nama:</b> {row['name_station']}<br>
    <b>Jenis:</b> {alat}<br>
    <b>Provinsi:</b> {row['nama_propinsi']}<br>
    <b>Kota:</b> {row['nama_kota']}<br>
    <b>Status:</b> {row.get('status_operasional', '')}<br>
    <b>Instansi:</b> {row.get('instansi', '')}
    """

    folium.Marker(
        location=[lat, lon],
        popup=popup,
        icon=folium.Icon(color=warna["color"], icon=warna["icon"], prefix="glyphicon")
    ).add_to(prov_cluster)

# Tampilkan peta
st.subheader("🗺️ Peta Lokasi Alat")
st_folium(m, width=1000, height=600)

# ------------------- Summary Alat -------------------
st.subheader("📊 Ringkasan Jumlah Alat per Provinsi dan Jenis")
summary = df_filtered.groupby(["nama_propinsi", "jenis_alat"]).size().reset_index(name="jumlah")
total_alat = summary["jumlah"].sum()
st.dataframe(summary, use_container_width=True)
st.markdown(f"**Total seluruh alat yang ditampilkan:** {total_alat}")

# Unduh PDF
st.subheader("📄 Download PDF Alat Pengamatan")
pdf_folder = "file_peta"
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
for pdf in pdf_files:
    with open(os.path.join(pdf_folder, pdf), "rb") as f:
        st.download_button(label=f"Unduh {pdf}", data=f, file_name=pdf)

