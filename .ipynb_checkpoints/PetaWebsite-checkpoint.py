#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from io import BytesIO

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_excel('data/peralatan_klimatologi.xlsx')

data = load_data()

# --- Sidebar untuk filtering ---
st.sidebar.title("Filter Data")
jenis_filter = st.sidebar.multiselect("Pilih Jenis Alat", options=data["Jenis"].unique(), default=data["Jenis"].unique())
provinsi_filter = st.sidebar.multiselect("Pilih Provinsi", options=data["Provinsi"].unique(), default=data["Provinsi"].unique())

# --- Filter data sesuai pilihan user ---
filtered_data = data[
    (data["Jenis"].isin(jenis_filter)) &
    (data["Provinsi"].isin(provinsi_filter))
]

# --- Judul ---
st.title("Peta Interaktif Jaringan Peralatan Klimatologi")

# --- Buat peta ---
m = folium.Map(location=[-2.5, 117], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

# --- Tambahkan marker ke peta ---
for i, row in filtered_data.iterrows():
    popup_info = f"""
    <b>Nama:</b> {row['Nama']}<br>
    <b>Jenis:</b> {row['Jenis']}<br>
    <b>Provinsi:</b> {row['Provinsi']}
    """
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup_info,
        icon=folium.Icon(color="blue", icon="cloud")
    ).add_to(marker_cluster)

# --- Tampilkan peta di Streamlit ---
st_data = st_folium(m, width=800, height=500)

# --- Tombol Download File PDF ---
st.markdown("### Unduh Peta Statis (PDF dari ArcGIS)")
with open("static/peta_statis_arcgis.pdf", "rb") as f:
    pdf_data = f.read()

st.download_button(
    label="📥 Download Peta Statis (PDF)",
    data=pdf_data,
    file_name="peta_klimatologi_arcgis.pdf",
    mime="application/pdf"
)

